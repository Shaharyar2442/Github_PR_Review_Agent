from fastapi import APIRouter
from pydantic import BaseModel
from langgraph.types import Command
from agent.graph import graph

router = APIRouter()

class ApprovalRequest(BaseModel):
    thread_id: str
    status: str # "approved" or "rejected"


@router.post("/approve")
def approve(request: ApprovalRequest):
    config = {"configurable": {"thread_id": request.thread_id}}
    graph.invoke(Command(resume=request.status), config=config)
    return {"message": f"Graph resumed with status: {request.status}"}
    

@router.get("/pending")
def pending():
    threads = graph.checkpointer.list(None)
    pending = []
    for thread in threads:
        snapshot = graph.get_state(thread.config)
        if snapshot.next == ("human_approval",):
            state = snapshot.values
            pending.append({
                "thread_id": snapshot.config["configurable"]["thread_id"],
                "owner": state.get("owner"),
                "repo": state.get("repo"),
                "pr_number": state.get("pr_number"),
                "issues": state.get("issues", []),
                "suggestions": state.get("suggestions", [])
            })
    return {"pending_reviews": pending}
