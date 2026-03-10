from agents.base_agent import BaseAgent

class AssetAgent(BaseAgent):
    """
    Answers questions about art assets, prefabs, and materials in the game.
    """

    def __init__(self, game_name: str = None):

        # Set up the agent with its name and which game it's working with
        super().__init__(
            name="AssetAgent",
            description="Analyzes art assets, prefabs, materials, and animations in the game repository",
            game_name=game_name
        )

    def build_system_prompt(self) -> str:

        # Tell Claude to act as an asset expert for this specific game
        return f"""You are an expert art asset analyst for the game '{self.game_name}'.

        Your job is to help game developers understand the asset library by:
        1. Explaining what assets exist and how they are used in the game
        2. Identifying which prefabs, materials, and animations belong to which characters or scenes
        3. Describing how assets are configured and connected to game logic
        4. Answering questions about specific assets or asset organization

        When given asset or prefab context, always reference specific asset names and their properties.
        Keep your answers clear and practical for a game development team."""