import os
from agents.character_agent import CharacterAgent

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

# Create the agent for this game
agent = CharacterAgent(game_name = "Capybara vs. Granny")

# Ask a question focused on character behavior and interactions
response = agent.ask(
    question = "What characters exist in this game, what are their behaviors, and how do they interact with each other?",
    context = codebase_context
)

print(response)