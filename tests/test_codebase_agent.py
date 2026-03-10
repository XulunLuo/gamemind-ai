import os
from agents.codebase_agent import CodebaseAgent

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
agent = CodebaseAgent(game_name = "Capybara vs. Granny")

# Ask a question that requires understanding multiple files
response = agent.ask(
    question = "How does the Granny chase the player, and what happens when she catches them?",
    context = codebase_context
)

print(response)