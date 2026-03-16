from projects.game_project import register
from core.orchestrator import Orchestrator

print("=== GameMind End-to-End Test ===\n")

# Step 1 — Register the game
print("Registering game...")
project = register(name = "Capybaras-vs.-Granny")
print(f"Registered: {project.name}\n")

# Step 2 — Create the orchestrator
orchestrator = Orchestrator(project = project)

# Step 3 — Ask three questions covering different domains
questions = [
    "How does Granny chase the player?",
    "How does GrannyController work?",
    "What characters are in this game?",
    "What scenes or levels does this game have?"
]

for question in questions:
    print(f"Q: {question}")
    answer = orchestrator.ask(question)
    print(f"A: {answer}")
    print("-" * 50)
