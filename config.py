import os 
from dotenv import load_dotenv

load_dotenv()

# Anthropic
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MODEL = "claude-sonnet-4-20250514"

# Discord
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# ChromaDB
CHROMA_DB_PATH = "./chroma_db"

# Game projects 
GAMES_BASE_PATH = os.getenv("GAMES_BASE_PATH", "./gameprojects")