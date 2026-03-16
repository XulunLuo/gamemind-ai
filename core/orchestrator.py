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
            1. codebase  — scripts, code logic, functions, game mechanics implementation
            2. character — specific characters, enemies, behaviors, stats, AI logic
            3. world     — scene names, level layout, spawn points, environment, fog settings
            4. asset     — art assets, prefabs, materials, animations, textures
            5. overview  — game type, player count, general description, how to play, game summary

            Examples:
            Q: "How does the dash ability work?"         → codebase
            Q: "What is Granny's attack range?"          → character
            Q: "What scenes does this game have?"        → world
            Q: "What 3D models are in this game?"        → asset
            Q: "Is this a multiplayer game?"             → overview
            Q: "Give me an introduction to this game"    → overview
            Q: "How many players can play?"              → overview
            Q: "What kind of game is this?"              → overview
            Q: "How is the game played?"                 → overview

            Reply with only one word: codebase, character, world, asset, or overview.""",
                        messages = [{"role": "user", "content": question}]
                    )

        domain = response.content[0].text.strip().lower().strip(".,\n ")

        if domain not in self.agents and domain != "overview":
            print(f"[Orchestrator] Unexpected domain '{domain}', falling back to codebase")
            domain = "codebase"

        return domain

    def ask(self, question: str) -> str:
        """Classify the question, fetch domain specific context, route to the right agent."""

        domain = self.classify(question)
        print(f"[Orchestrator] Routing to: {domain}")

        # Overview questions search across all domains
        if domain == "overview":
            context = query_collection(
                game_name = self.project.name,
                question = question,
                domain = None
            )
            return self.agents["codebase"].ask(question=question, context=context)

        context = query_collection(
            game_name = self.project.name,
            question = question,
            domain = domain
        )

        return self.agents[domain].ask(question=question, context=context)





