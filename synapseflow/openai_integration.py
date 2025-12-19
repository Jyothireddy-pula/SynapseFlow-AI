import os, sys, time
from typing import Iterator, Dict, Any, Optional

try:
    import openai
except Exception:
    openai = None

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY') or ''
OPENAI_API_BASE = os.getenv('OPENAI_API_BASE') or None
OPENAI_MODEL = os.getenv('OPENAI_MODEL') or 'gpt-4o-mini'

if openai and OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY
    if OPENAI_API_BASE:
        openai.api_base = OPENAI_API_BASE

def chat_completion(prompt: str, model: str = None, max_tokens: int = 300, temperature: float = 0.2) -> Dict[str, Any]:
    model = model or OPENAI_MODEL
    if openai is None:
        raise RuntimeError('openai package not installed. pip install openai')
    if not OPENAI_API_KEY:
        raise RuntimeError('OPENAI_API_KEY not set in environment (.env)')
    resp = openai.ChatCompletion.create(
        model=model,
        messages=[{'role':'system','content':'You are a helpful assistant.'},
                  {'role':'user','content':prompt}],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    text = ''
    for choice in getattr(resp, 'choices', []):
        msg = choice.get('message') if isinstance(choice, dict) else getattr(choice, 'message', None)
        if msg:
            content = msg.get('content') if isinstance(msg, dict) else getattr(msg, 'content', '')
            text += content or ''
    return {'text': text, 'raw': resp}

def chat_stream(prompt: str, model: str = None, max_tokens: int = 300, temperature: float = 0.2) -> Iterator[str]:
    model = model or OPENAI_MODEL
    if openai is None:
        raise RuntimeError('openai package not installed. pip install openai')
    if not OPENAI_API_KEY:
        raise RuntimeError('OPENAI_API_KEY not set in environment (.env)')
    # streaming API returns an iterator of events
    stream = openai.ChatCompletion.create(
        model=model,
        messages=[{'role':'system','content':'You are a helpful assistant.'},
                  {'role':'user','content':prompt}],
        max_tokens=max_tokens,
        temperature=temperature,
        stream=True,
    )
    for event in stream:
        try:
            # event structure varies by provider; attempt safe extraction
            choices = event.get('choices') if isinstance(event, dict) else getattr(event, 'choices', None)
            if choices:
                delta = choices[0].get('delta') if isinstance(choices[0], dict) else getattr(choices[0], 'delta', {})
                content = delta.get('content') if isinstance(delta, dict) else getattr(delta, 'content', None)
                if content:
                    yield content
        except Exception:
            # fallback to stringified event chunk
            yield str(event)


def get_embedding(text: str, model: str = 'text-embedding-3-small') -> list:
    """Return embedding vector for `text` using OpenAI embeddings API."""
    if openai is None:
        raise RuntimeError('openai package not installed. pip install openai')
    if not OPENAI_API_KEY:
        raise RuntimeError('OPENAI_API_KEY not set in environment (.env)')
    try:
        resp = openai.Embedding.create(model=model, input=[text])
        emb = resp['data'][0]['embedding'] if isinstance(resp, dict) else resp.data[0].embedding
        return emb
    except Exception as e:
        raise RuntimeError('Embedding call failed: ' + str(e))
