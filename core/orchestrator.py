from anthropic import Anthropic
from config import ANTHROPIC_API_KEY, MODEL, GAME_NAME
from agents.asset_agent import AssetAgent
from agents.character_agent import CharacterAgent
from agents.codebase_agent import CodebaseAgent
from agents.world_agent import WorldAgent

class Orchestrator:
    """
    Routes user questions to the right specialized agent.
    """

    def __init__(self, game_name: str = GAME_NAME, context: str = ""):

        # One Claude agent for a routing decisions
        self.client = Anthropic(api_key = ANTHROPIC_API_KEY)
        self.game_name = game_name

        # The shared loaded game files passed to every agent
        self.context = context

        # Initialize for the four agents
        self.agents = {
            "asset": AssetAgent(game_name = game_name),
            "character": CharacterAgent(game_name = game_name),
            "codebase": CodebaseAgent(game_name = game_name),
            "world": WorldAgent(game_name = game_name)
        }

    def classify(self, question: str) -> str:
        """Ask Claude which domain this question belongs to."""

        response = self.client.messages.create (
            model = MODEL,
            max_tokens = 20,
            system = 
            """You are a router for a game AI system. 
            Classify the user's question into exactly one of these domains:
            1. codebase  (scripts, code logic, game mechanics, functions)
            2. character (characters, enemies, behaviors, stats, AI logic)
            3. world     (level structure, scene names, spawn points, level progression, win/lose conditions, environment layout)
            4. asset     (art assets, prefabs, materials, animations, textures)

            Reply with only one word: codebase, character, world, or asset.""",
            messages = [{"role": "user", "content": question}]
        ) 
        
        domain = response.content[0].text.strip().lower()

        # Fallback handler to the codebase if Claude reply something unexpected
        if domain not in self.agents:
            raise ValueError(f"[Orchestrator] Unknown domain '{domain}' returned by classifier")

        return domain
    
    def ask(self, question: str) -> str:
        """Classify the question, route it to the right agent, and return the answer."""

        domain = self.classify(question)
        print(f"[Orchestrator] Routing to: {domain}")

        agent = self.agents[domain]
        return agent.ask(question = question, context = self.context)





