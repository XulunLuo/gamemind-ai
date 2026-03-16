import os
from config import GAMES_BASE_PATH
from projects.unity_loader import load_files_by_domain, load_all_as_string
from ingestion.indexer import index_project

# Maps project name to GameProject 
_registry: dict = {}

class GameProject:
    """
    Represents a single named game project with its own isolated file context.
    Each project knows its name, engine, and where its files live on disk.
    """

    def __init__(self, name: str, path: str, engine: str = "unity"):
        self.name = name 
        self.path = path
        self.engine = engine

        # Create a domain to be loaded
        self.context_by_domain: dict = {}

    def load(self):
        """
        Read all game files from disk and store them grouped by domain.
        """

        if self.engine == "unity":
            self.context_by_domain = load_files_by_domain(self.path)
            index_project(self.name, self.path)
        else:
            raise ValueError(f"Unsupported engine: '{self.engine}'. Only 'unity' is supported.")
        
        # Check if there are acutally files in certain domain
        domains_with_content = []
        
        for domain, content in self.context_by_domain.items():
            if content.strip():
                domains_with_content.append(domain)
        
        total_domains = len(domains_with_content)
        print(f"Loaded '{self.name}' with {total_domains} domain(s) of content")

    def get_context(self, domain: str = None) -> str:
        """
        Return file context for a specific domain, or all domains combined.
        """

        if not self.context_by_domain:
            raise RuntimeError(f"[GameProject] Project '{self.name}' has not been loaded. Call .load() first.")

        if domain:
            return self.context_by_domain.get(domain, "")
        
        return "\n\n".join(self.context_by_domain.values())
    
# Registry functions 
def register(name: str, engine: str = "unity") -> GameProject:
    """Create a GameProject, load its files, and add it to the registry."""

    path = os.path.join(GAMES_BASE_PATH, name)

    if not os.path.isdir(path):
        
        available = [
            f for f in os.listdir(GAMES_BASE_PATH)
            if os.path.isdir(os.path.join(GAMES_BASE_PATH, f))
            and not f.startswith(".")
        ]

        raise ValueError(
            f"Game '{name}' not found in {GAMES_BASE_PATH}.\n"
            f"Available games: {', '.join(available)}"
        )

    project = GameProject(name = name, path = path, engine = engine)
    project.load()
    _registry[name] = project
    return project


def get(name: str) -> GameProject:
    """Retrieve a registered project by name."""

    if name not in _registry:
        raise KeyError(f"No project registered under '{name}'.")
    return _registry[name]


def list_projects() -> list:
    """Return the names of all registered projects."""

    return list(_registry.keys())