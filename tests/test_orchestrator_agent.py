import os
from core.orchestrator import Orchestrator

def load_codebase(folder_path: str) -> str:

    """Read all .cs files from a folder and combine them into one context string"""
    context = ""
    for filename in os.listdir(folder_path):
        if filename.endswith(".cs"):
            filepath = os.path.join(folder_path, filename)
            with open(filepath, "r") as f:
                content = f.read()
                context += f"\n\n// === {filename} ===\n{content}"
    return context

# Load all sample C# files
codebase_context = load_codebase("data/sample_code")

# Create the orchestrator with shared context
orchestrator = Orchestrator(game_name="Capybara vs. Granny", context=codebase_context)

# Each should route to a different agent
questions = [
    "How does the score system work?",                         # codebase
    "How does Granny chase and attack the player?",            # character
    "How do levels load and what triggers a game over?",       # world
]

for question in questions:
    print(f"\nQ: {question}")
    response = orchestrator.ask(question)
    print(response)