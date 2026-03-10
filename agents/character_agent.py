from agents.base_agent import BaseAgent

class CharacterAgent(BaseAgent):
    """
    Answers questions about characters and entities in the game.
    """

    def __init__(self, game_name: str = None):

        # Set up the agent with its name and which game it's working with
        super().__init__(
            name="CharacterAgent",
            description="Analyzes characters, enemies, and entities in the game repository",
            game_name=game_name
        )

    def build_system_prompt(self) -> str:

        # Tell Claude to act as a character/entity expert for this specific game
        return f"""You are an expert character and entity analyst for the game '{self.game_name}'.

        Your job is to help game developers understand all characters and entities by:
        1. Explaining character behaviors, stats, and abilities in plain English
        2. Identifying how characters interact with each other and with the player
        3. Describing AI logic — how enemies move, attack, and react
        4. Answering questions about specific characters or entity types

        When given code or config context, always reference the specific character names and script logic.
        Keep your answers clear and practical for a game development team."""