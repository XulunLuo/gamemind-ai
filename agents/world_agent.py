from agents.base_agent import BaseAgent

class WorldAgent(BaseAgent):
    """
    Answers questions about scenes, levels, and world structure in the game.
    """

    def __init__(self, game_name: str = None):

        # Set up the agent with its name and which game it's working with
        super().__init__(
            name="WorldAgent",
            description="Analyzes scenes, level layout, and world structure in the game repository",
            game_name=game_name
        )

    def build_system_prompt(self) -> str:

        # Tell Claude to act as a world/level expert for this specific game
        return f"""You are an expert world and level design analyst for the game '{self.game_name}'.

        Your job is to help game developers understand the game world by:
        1. Explaining how scenes and levels are structured and connected
        2. Describing spawn points, boundaries, and environment rules
        3. Identifying how the world reacts to player actions and game state
        4. Answering questions about specific levels or world systems

        When given code or config context, always reference specific scene names and level logic.
        Keep your answers clear and practical for a game development team."""