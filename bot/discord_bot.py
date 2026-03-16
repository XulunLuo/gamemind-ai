import discord
from discord.ext import commands
from config import DISCORD_BOT_TOKEN
from projects.game_project import register, get, list_projects, list_available_games
from core.orchestrator import Orchestrator

# Bot setup 
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix = "!", intents = intents)

# One orchestrator shared across all commands
_orchestrator: Orchestrator = None


@bot.event
async def on_ready():
    print(f"[GameMind Bot] Logged in as {bot.user}")


@bot.command(name = "games")
async def list_available(ctx):
    """List all games available to register."""

    try:
        available = list_available_games()
    except Exception as e:
        await ctx.send(f"Could not read games folder: `{e}`")
        return

    if not available:
        await ctx.send("No games found in the games folder.")
    else:
        await ctx.send(f"Available games to register: `{', '.join(available)}`")


@bot.command(name = "register")
async def register_project(ctx, name: str):
    """
    Register a game project and load its files.
    Example Usage: !register Capybaras-vs.-Granny
    """
    await ctx.send(f"Loading project **{name}**...")

    try:
        project = register(name = name)
        domains = list(project.context_by_domain.keys())
        await ctx.send(f"Registered **{project.name}** and domains loaded: `{', '.join(domains)}`")
    except Exception as e:
        await ctx.send(f"Failed to register project: `{e}`")


@bot.command(name = "projects")
async def list_all_projects(ctx):
    """
    List all registered game projects.
    """
    names = list_projects()

    if not names:
        await ctx.send("No projects registered yet. Use `!register <name>` to add one.")
    else:
        await ctx.send(f"Registered projects: `{', '.join(names)}`")


@bot.command(name = "ask")
async def ask(ctx, project: str, *, question: str):
    """
    Ask a question about a registered game project.
    """
    global _orchestrator

    # Look up the project
    try:
        proj = get(project)
    except KeyError:
        await ctx.send(f"No project registered under `{project}`. Use `!projects` to see what's loaded.")
        return

    # Let the user know it's working
    async with ctx.typing():
        if _orchestrator is None:
            _orchestrator = Orchestrator(project = proj)
        elif _orchestrator.project.name != project:
            _orchestrator.set_project(proj)

        try:
            answer = _orchestrator.ask(question)
        except Exception as e:
            await ctx.send(f"Something went wrong: `{e}`")
            return

    await ctx.send(f"**[{proj.name}]** {answer}")


if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN)
