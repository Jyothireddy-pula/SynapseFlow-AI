# 2-3 Minute Demo Script for SynapseFlow Final

Intro (0:00-0:10)
- Title: SynapseFlow — Final
- One-line pitch: "An extensible multi-agent framework with planning, memory, tools, and streaming LLM integration."

Demo 1 (0:10-0:50) — run_demo.py
- Show terminal, run `python run_demo.py`
- Point out tool discovery and planner output (trip planning + weather + stock).

Demo 2 (0:50-1:30) — streaming
- Run `python stream_demo.py` (requires OPENAI_API_KEY)
- Explain streaming chunks and low-latency behavior.

Demo 3 (1:30-2:10) — Qdrant demo (optional)
- Start Qdrant via docker-compose (show command).
- Run `python qdrant_demo.py` and explain upsert/query flows.

Close (2:10-2:30)
- Summarize features and next steps (embed, UI, productionize).
- Provide GitHub link & invite contributions.
