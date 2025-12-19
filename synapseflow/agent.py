import os, time, json, re
from typing import Callable, List, Dict, Any, Optional

# Simple Tool wrapper
class Tool:
    def __init__(self, name: str, func: Callable, description: str = '', params: Optional[List[Dict[str,str]]] = None):
        self.name = name
        self.func = func
        self.description = description or ''
        self.params = params or []

    def run(self, *args, **kwargs):
        return self.func(*args, **kwargs)

# Memory (file-backed) with adapter hook (e.g., Qdrant)
class Memory:
    def __init__(self, path: str = 'memory.json', adapter: Any = None):
        self.path = path
        self.adapter = adapter
        try:
            with open(self.path, 'r') as f:
                self._data = json.load(f)
        except Exception:
            self._data = {}

        # If no adapter provided and QDRANT_URL env exists, attempt to init adapter lazily
        if not self.adapter and os.getenv('QDRANT_URL'):
            try:
                from .qdrant_adapter import QdrantAdapter
                self.adapter = QdrantAdapter(url=os.getenv('QDRANT_URL'))
            except Exception as e:
                print('QdrantAdapter init failed:', e)

    def add(self, user_id: str, text: str, meta: dict = None):
        rec = {'t': time.time(), 'text': text, 'meta': meta or {}}
        self._data.setdefault(user_id, []).append(rec)
        try:
            with open(self.path, 'w') as f:
                json.dump(self._data, f, indent=2)
        except Exception as e:
            print('Failed to write memory file:', e)
        # push to adapter if available
        if self.adapter:
            try:
                import os
                if os.getenv('USE_EMBEDDINGS_QDRANT') == '1':
                    try:
                        from .embeddings_qdrant import EmbeddingMemory
                        embm = EmbeddingMemory()
                        embm.upsert_text(user_id, text, meta or {})
                        return
                    except Exception as e:
                        print('EmbeddingMemory upsert failed:', e)
                # fallback to regular adapter upsert
                self.adapter.upsert(user_id, text, meta or {})
            except Exception as e:
                print('Memory adapter upsert failed:', e)

    def query(self, user_id: str, q: str, top_k: int = 5):
        # naive keyword match + recency boost
        items = self._data.get(user_id, [])
        qset = set(q.lower().split())
        scored = []
        for it in items:
            words = set(it.get('text','').lower().split())
            score = len(qset & words)
            # recency boost
            score += 0.000001 * (time.time() - it['t'])
            if score > 0:
                scored.append((score, it))
        scored.sort(reverse=True, key=lambda x: x[0])
        return [s[1] for s in scored[:top_k]]

# Planner: Tree-of-Thought style simple planner
class Planner:
    @staticmethod
    def plan(task: str) -> List[str]:
        parts = re.split(r'[.;\n]| and | then ', task)
        parts = [p.strip() for p in parts if p.strip()]
        if not parts:
            return [task]
        refined = []
        for p in parts:
            if len(p.split()) > 40:
                refined.extend([x.strip() for x in re.split(r'[,:]', p) if x.strip()])
            else:
                refined.append(p)
        # if still single long part split roughly
        if len(refined) == 1 and len(refined[0].split()) > 20:
            words = refined[0].split()
            half = len(words)//2
            refined = [' '.join(words[:half]), ' '.join(words[half:])]
        return refined

# Agent core
class Agent:
    def __init__(self, name: str = 'SynapseFlow', memory: Memory = None, trace: Callable[[dict],None] = None):
        self.name = name
        self.tools: Dict[str, Tool] = {}
        self.memory = memory or Memory()
        self.trace = trace
        self.history: List[Dict[str,Any]] = []

    def register_tool(self, tool: Tool):
        self.tools[tool.name] = tool

    def discover_tools(self, module_prefix: str = 'synapseflow.tools'):
        import pkgutil, importlib
        try:
            pkg = importlib.import_module(module_prefix)
        except Exception as e:
            print('Tool discovery failed:', e)
            return
        for finder, name, ispkg in pkgutil.iter_modules(pkg.__path__):
            try:
                mod = importlib.import_module(f"{module_prefix}.{name}")
                # find callable functions and metadata
                funcs = [a for a in dir(mod) if callable(getattr(mod, a)) and not a.startswith('_')]
                if not funcs:
                    continue
                func = getattr(mod, funcs[0])
                tname = getattr(mod, 'tool_name', funcs[0])
                desc = getattr(mod, 'tool_description', '')
                params = getattr(mod, 'tool_params', None)
                self.register_tool(Tool(tname, func, desc, params))
            except Exception as e:
                print('Failed loading tool module', name, e)

    def select_tools(self, query: str, top_n: int = 3):
        # simple scoring: count of token occurrences in tool name+description
        qtokens = query.lower().split()
        scores = []
        for tname, t in self.tools.items():
            text = (t.description + ' ' + tname).lower()
            score = sum(text.count(q) for q in qtokens)
            if any(q in tname.lower() for q in qtokens):
                score += 1
            scores.append((score, t))
        scores.sort(reverse=True, key=lambda x: x[0])
        selected = [t for s,t in scores if s>0]
        if not selected:
            selected = [t for _,t in scores[:top_n]]
        return selected[:top_n]

    def run_step(self, step: str):
        tools = self.select_tools(step)
        outs = []
        for t in tools:
            try:
                out = t.run(step)
            except Exception as e:
                out = f"Tool {t.name} failed: {e}"
            outs.append({'tool': t.name, 'output': out})
            if self.trace:
                try:
                    self.trace({'step': step, 'tool': t.name, 'output': str(out)})
                except Exception:
                    pass
        return outs

    def run(self, user_id: str, query: str, use_planner: bool = True):
        entry = {'user': user_id, 'query': query, 'time': time.time()}
        self.history.append(entry)
        try:
            self.memory.add(user_id, query)
        except Exception as e:
            print('Memory add failed:', e)
        steps = Planner.plan(query) if use_planner else [query]
        final = []
        for s in steps:
            res = self.run_step(s)
            final.append({'step': s, 'results': res})
        return final

# Multi-agent orchestrator (LightSwarm)
class LightSwarm:
    def __init__(self):
        self.agents: Dict[str, Agent] = {}

    def register_agent(self, agent: Agent):
        self.agents[agent.name] = agent

    def run(self, agent_name: str, query: str):
        agent = self.agents.get(agent_name)
        if not agent:
            return {'error': 'agent not found'}
        return agent.run('swarm_user', query)
