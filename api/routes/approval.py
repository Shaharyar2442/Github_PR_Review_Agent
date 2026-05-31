from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from langgraph.types import Command
from agent.graph import get_graph
from api.routes.auth import get_current_user
from loguru import logger

router = APIRouter()


class ApprovalRequest(BaseModel):
    thread_id: str
    status: str  # "approved" or "rejected"


@router.post("/approve")
async def approve(request: ApprovalRequest, current_user: dict = Depends(get_current_user)):
    graph = get_graph()
    config = {"configurable": {"thread_id": request.thread_id}}
    await graph.ainvoke(Command(resume=request.status), config=config)
    return {"message": f"Graph resumed with status: {request.status}"}


@router.get("/pending")
async def pending(current_user: dict = Depends(get_current_user)):
    try:
        graph = get_graph()
        pending_list = []

        # Get all unique thread IDs to avoid looking at historical ghost states
        threads_generator = graph.checkpointer.alist(None)
        unique_thread_ids = set([t.config["configurable"]["thread_id"] async for t in threads_generator])

        for tid in unique_thread_ids:
            # Passing only thread_id fetches the absolute latest state
            snapshot = await graph.aget_state({"configurable": {"thread_id": tid}})
            if snapshot.next == ("human_approval",):
                state = snapshot.values
                if state.get("owner") == current_user.get("github_username"):
                    pending_list.append({
                        "thread_id": snapshot.config["configurable"]["thread_id"],
                        "owner": state.get("owner"),
                        "repo": state.get("repo"),
                        "pr_number": state.get("pr_number"),
                        "issues": state.get("issues", []),
                        "suggestions": state.get("suggestions", [])
                    })
        return {"pending_reviews": pending_list}
    except Exception as e:
        # Log the full traceback server-side, return generic error to client (#4)
        logger.exception("Error fetching pending reviews")
        raise HTTPException(status_code=500, detail="Internal server error")
