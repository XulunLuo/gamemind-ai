import os 
from dotenv import load_dotenv

load_dotenv()

# Anthropic
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MODEL = ""

# Discord
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# ChromaDB
CHROMA_DB_PATH = "./chroma_db"

# Game project
GAME_NAME = "Capybara vs. Granny"
CODEBASE_PATH = "./data/sample_code"  # dummy data 