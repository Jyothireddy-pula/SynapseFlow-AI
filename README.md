# SynapseFlow — Production-Ready Agent Framework 

**Overview**: SynapseFlow is an extensible multi-agent framework that can plan, use tools, remember conversations, and stream LLM responses. This package is a complete, well-documented, and demo-ready project that you can run locally and extend for production use.


## Highlights
- Modular Agent core (Planner, Memory, Tool Registry)
- OpenAI integration (sync + streaming) with example consumer
- Qdrant adapter for vector memory (optional)
- Tool generator that creates safe Python tool stubs
- FastAPI HTTP server with a streaming endpoint and demo UI hooks
- Dockerfile + docker-compose for Qdrant
- Demo scripts, tests, CI, README, demo GIF placeholder, demo script, and storyboard
- MIT license — reuse and extend

## Quick start (exact commands)
1. Unzip project and `cd synapseflow_final_10`
2. Create Python venv and activate:
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and set `OPENAI_API_KEY` if you want streaming demos. Optionally set `QDRANT_URL` for memory.
4. Run basic demo (no API keys required):
   ```bash
   python run_demo.py
   ```
5. Run streaming demo (requires `OPENAI_API_KEY`):
   ```bash
   python stream_demo.py
   ```
6. Run Qdrant demo (requires Qdrant):
   ```bash
   docker compose -f docker-compose.qdrant.yml up -d
   python qdrant_demo.py
   ```
7. Run FastAPI server:
   ```bash
   uvicorn synapseflow_app:app --reload
   ```

## Project layout (top-level)
```
/synapseflow_final_10
├─ synapseflow/              # core package (Agent, tools, integrations)
├─ run_demo.py              # simple terminal demo
├─ stream_demo.py           # streaming LLM demo
├─ qdrant_demo.py           # Qdrant adapter demo
├─ synapseflow_app.py        # FastAPI HTTP server (with streaming)
├─ requirements.txt
├─ Dockerfile
├─ docker-compose.qdrant.yml
├─ README.md
├─ DEMO_SCRIPT.md
├─ VIDEO_STORYBOARD.md
├─ RESUME_BULLETS.md
└─ assets/demo.gif
```

## Support & Next steps
- Replace placeholder API keys in `.env`
- Add embedding model and wire into `synapseflow.qdrant_adapter` for full vector search
- Replace demo tools with production-grade APIs and error handling as required
- Add a front-end to consume the SSE streaming endpoint for a polished demo

---
If you want, I can now:
- Create an actual GIF (screen-recording frames) to replace `assets/demo.gif`
- Replace stubs with OpenAI embedding upserts into Qdrant (requires API key)
- Add an example frontend (simple HTML + JS) that consumes streaming SSE responses

Pick one and I will implement it directly into the zip.


# Embeddings -> Qdrant
Set `USE_EMBEDDINGS_QDRANT=1` in your .env to enable OpenAI embeddings upserts into Qdrant when Memory.add is called.


New features in this release:
- Frontend with auth and SSE streaming UX
- Embeddings->Qdrant end-to-end
- Deployment templates for Render and Railway
- MP4->GIF conversion script



## License

This project is licensed under the Apache-2.0 License. See LICENSE file for details.
