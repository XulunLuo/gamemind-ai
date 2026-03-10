from agents.base_agent import BaseAgent

class CodebaseAgent(BaseAgent):
    """
    Answers questions about Unity C# scripts.
    """

    def __init__(self, game_name: str = None):

        # Set up the agent with its name and which game it's working with
        super().__init__(
            name="CodebaseAgent",
            description="Analyzes and explains C# scripts in the game repository",
            game_name=game_name
        )

    def build_system_prompt(self) -> str:

        # Tell Claude to act as a code expert for this specific game
        return f"""You are an expert Unity C# code analyst for the game '{self.game_name}'.
        
        Your job is to help game developers understand the codebase by:
        1. Explaining what scripts and functions do in plain English
        2. Identifying how different systems connect to each other
        3. Spotting potential bugs or improvements
        4. Answering questions about specific scripts

        When given code context, always reference the specific script names and line logic.
        Keep your answers clear and practical for a game development team."""