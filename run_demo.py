from synapseflow.agent import Agent, Memory, Tool
import importlib, json

def wrap_mod(mod):
    funcs = [a for a in dir(mod) if callable(getattr(mod,a)) and not a.startswith('_')]
    func = getattr(mod, funcs[0])
    return Tool(getattr(mod, 'tool_name', funcs[0]), func, getattr(mod, 'tool_description', ''))

def main():
    mem = Memory(path='memory_demo.json')
    agent = Agent(memory=mem)
    # discover and register tools
    agent.discover_tools('synapseflow.tools')
    print('Tools registered:', list(agent.tools.keys()))
    query = 'Plan a short trip to Sanya and check weather and find stock INFY'
    res = agent.run('demo_user', query)
    print(json.dumps(res, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
