

class AgentWrapper:
    def __init__(self):
        self.agent = Agent(name="Assistant",
        instructions="You are a helpful financial assistant",
        tools=[WebSearchTool()])


    def get_agent_response(self, message: str) -> str:
        return self.agent.run(message)


    





