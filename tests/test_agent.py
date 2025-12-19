from lightagent.agent import Agent, Memory, Tool
def test_agent_run():
    mem = Memory(path='memory_test.json')
    agent = Agent(memory=mem)
    # register a dummy tool
    def echo(x): return 'ECHO:'+x
    agent.register_tool(Tool('echo', echo, 'echo tool'))
    res = agent.run('u1', 'echo hello')
    assert res and isinstance(res, list)
if __name__ == '__main__':
    test_agent_run()
    print('test passed')
