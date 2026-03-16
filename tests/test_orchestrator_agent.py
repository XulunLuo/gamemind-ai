from projects.game_project import register
from core.orchestrator import Orchestrator

# Register the game first — this loads files and indexes into ChromaDB
project = register(name="Capybaras-vs.-Granny")

# Create orchestrator with the project object
orchestrator = Orchestrator(project=project)

# Ask a test question
response = orchestrator.ask("How does Granny chase the player?")
print(response)
