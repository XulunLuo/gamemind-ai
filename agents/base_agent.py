from anthropic import Anthropic
from config import ANTHROPIC_API_KEY, MODEL

class BaseAgent:

    # Set the agent's name, description, and creates one Claude client for it
    def __init__(self, name: str, description: str, game_name: str = "Unknown Game"):
        self.name = name
        self.description = description
        self.game_name = game_name
        self.client = Anthropic(api_key = ANTHROPIC_API_KEY)

    def build_system_prompt(self) -> str:
        raise NotImplementedError("Each agent must define its own system prompt")
    
    def ask(self, question: str, context: str = "") -> str:

         # Get the system prompt from whichever child agent is calling this
        system_prompt = self.build_system_prompt()

        # Combine the game context + developer question into one message
        user_message = f"""Context from the game repository: {context} 
        Question: {question}"""

        # Send everything to Claude and get the response
        message = self.client.messages.create(
            model = MODEL,
            max_tokens = 1000,
            system = system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )

        return message.content[0].text


    