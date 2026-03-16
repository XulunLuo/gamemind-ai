from anthropic import Anthropic
from config import ANTHROPIC_API_KEY, MODEL
from agents.asset_agent import AssetAgent
from agents.character_agent import CharacterAgent
from agents.codebase_agent import CodebaseAgent
from agents.world_agent import WorldAgent
from projects.game_project import GameProject
from ingestion.indexer import query_collection

class Orchestrator:
    """
    Routes user questions to the right specialized agent.
    Accepts a GameProject so context is isolated per game and fetched by domain.
    """

    def __init__(self, project: GameProject):

        # One Claude client for routing decisions
        self.client = Anthropic(api_key = ANTHROPIC_API_KEY)
        self.project = project

        # Initialize the four agents with this project's name
        self.agents = {
            "asset": AssetAgent(game_name = project.name),
            "character": CharacterAgent(game_name = project.name),
            "codebase": CodebaseAgent(game_name = project.name),
            "world": WorldAgent(game_name = project.name)
        }

    def classify(self, question: str) -> str:
        """Ask Claude which domain this question belongs to."""

        response = self.client.messages.create(
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

        # Strip punctuation in case Claude returns "asset." or "world\n"
        domain = domain.strip(".,\n ")

        # Fallback to codebase if Claude returns something unexpected
        if domain not in self.agents:
            print(f"[Orchestrator] Unexpected domain '{domain}', falling back to codebase")
            domain = "codebase"

        return domain

    def ask(self, question: str) -> str:
        """Classify the question, fetch domain specific context, route to the right agent."""

        domain = self.classify(question)
        print(f"[Orchestrator] Routing to: {domain}")

        context = query_collection(
            game_name=self.project.name,
            question=question,
            domain=domain
        )

        agent = self.agents[domain]
        return agent.ask(question=question, context=context)





