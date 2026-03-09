from agents.base_agent import BaseAgent

# Create a simple system prompt for Claude API to build a simple agent
class TestAgent(BaseAgent):
    def build_system_prompt(self) -> str:
        return "You are a test agent for GameMind AI. Keep responses short."

# Run the test
agent = TestAgent(name="TestAgent", description="A simple test agent")
response = agent.ask("Say hello and tell me your name!")
print(response)
