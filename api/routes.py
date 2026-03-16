from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from projects.game_project import register, get, list_projects
from core.orchestrator import Orchestrator

app = FastAPI(title = "GameMind AI")

# One orchestrator per project 
_orchestrators: dict = {}


# Request / Response shapes
class RegisterRequest(BaseModel):
    name: str

class AskRequest(BaseModel):
    project: str    # which registered project to query
    question: str   # the developer's question

# Endpoints
@app.post("/projects/register")
def register_project(body: RegisterRequest):
    """
    Register a game project and load its files from disk.
    """
    
    try:
        project = register(name = body.name)
        return {"registered": project.name, "domains": list(project.context_by_domain.keys())}
    except Exception as e:
        raise HTTPException(status_code = 400, detail = str(e))


@app.get("/projects")
def get_projects():
    """List all registered game projects."""

    return {"projects": list_projects()}


@app.post("/ask")
def ask(body: AskRequest):
    """
    Ask a question about a registered game project.
    """

    global _orchestrators

    try:
        project = get(body.project)
    except KeyError:
        raise HTTPException(status_code = 404, detail = f"No project registered under '{body.project}'.")

    if body.project not in _orchestrators:
        _orchestrators[body.project] = Orchestrator(project=project)

    answer = _orchestrators[body.project].ask(body.question)
    return {"project": body.project, "answer": answer}
