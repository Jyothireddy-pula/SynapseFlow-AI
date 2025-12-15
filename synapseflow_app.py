import jwt
import time
import os, json, importlib
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from synapseflow.agent import Agent, Memory, Tool

app = FastAPI(title='SynapseFlow Final API')

from fastapi.staticfiles import StaticFiles
app.mount('/frontend', StaticFiles(directory='frontend'), name='frontend')


# initialize agent
mem = Memory(path='memory_api.json')
agent = Agent(memory=mem)
agent.discover_tools('synapseflow.tools')

class Query(BaseModel):
    user_id: str
    query: str

@app.post('/run')
def run_query(q: Query):
    res = agent.run(q.user_id, q.query)
    return JSONResponse({'result': res})

@app.post('/stream')
def stream_query(q: Query):
    # stream LLM response for the whole query by delegating to openai_integration.chat_stream
    try:
        from synapseflow.openai_integration import chat_stream
    except Exception as e:
        return JSONResponse({'error': 'openai integration not available: ' + str(e)})
    def iter_chunks():
        try:
            for chunk in chat_stream(q.query):
                yield chunk
        except Exception as e:
            yield '\n[stream error] ' + str(e)
    return StreamingResponse(iter_chunks(), media_type='text/plain')


from fastapi import Response

@app.get('/sse_stream')
async def sse_stream(request: Request):
    try:
        from synapseflow.openai_integration import chat_stream
    except Exception as e:
        return JSONResponse({'error': 'openai integration not available: ' + str(e)})

    async def event_generator(qstr: str):
        # stream chat chunks
        try:
            for chunk in chat_stream(qstr):
                yield f"data: {chunk}\n\n"
                # no native request.client_disconnected, so we don't check
        except Exception as e:
            yield f"data: [stream error] {str(e)}\n\n"

    q = request.query_params.get('q','')
    return StreamingResponse(event_generator(q), media_type='text/event-stream')

# Simple auth: HMAC JWT (demo only)
JWT_SECRET = 'synapseflow_secret_demo_change_me'
JWT_ALGO = 'HS256'

def create_token(username: str):
    payload = {'sub': username, 'iat': int(time.time()), 'exp': int(time.time()) + 3600}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)

@app.post('/auth/token')
def auth_token(req: Request):
    data = req.json() if hasattr(req, 'json') else None
    try:
        body = req.json()
    except Exception:
        # fallback parse
        import json
        body = json.loads(req._body.decode() if hasattr(req, '_body') else '{}')
    username = body.get('username')
    password = body.get('password')
    # demo credentials: username == password
    if not username or not password or username != password:
        raise HTTPException(status_code=401, detail='Invalid credentials')
    token = create_token(username)
    return {'access_token': token}

# modify sse_stream to accept token param and validate
from fastapi import Query

@app.get('/sse_stream')
async def sse_stream(request: Request, q: str = '', token: str = Query(None)):
    # validate token
    try:
        if not token:
            raise HTTPException(status_code=401, detail='missing token')
        jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    except Exception as e:
        return JSONResponse({'error':'invalid token: '+str(e)}, status_code=401)
    try:
        from synapseflow.openai_integration import chat_stream
    except Exception as e:
        return JSONResponse({'error': 'openai integration not available: ' + str(e)})
    async def event_generator(qstr: str):
        try:
            for chunk in chat_stream(qstr):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            yield f"data: [stream error] {str(e)}\n\n"
    return StreamingResponse(event_generator(q), media_type='text/event-stream')
