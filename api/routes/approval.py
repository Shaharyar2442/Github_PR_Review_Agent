from fastapi import APIRouter
from pydantic import BaseModel
from langgraph.types import Command
from agent.graph import graph

router = APIRouter()

class ApprovalRequest(BaseModel):
    thread_id: str
    status: str # "approved" or "rejected"

# ─── YOUR TURN (PHASE 5) ──────────────────────────────────────
# Goal: Build an endpoint to resume our paused LangGraph agent.
# Hint:
# 1. Create a `POST /approve` endpoint that accepts an `ApprovalRequest` body.
# 2. Build the config exactly like we did in `agent/graph.py`'s test block:
#    `config = {"configurable": {"thread_id": request.thread_id}}`
# 3. Call `await graph.ainvoke(Command(resume=request.status), config=config)`
# 4. Return a success dictionary: `{"message": f"Graph resumed with status: {request.status}"}`
# Expected result: Sending a JSON POST to this endpoint resumes the agent!
# ────────────────────────────────────────────────────────────

# TODO: Add your approval route here!
@router.post("/approve")
async def approve(request: ApprovalRequest):
    config = {"configurable": {"thread_id": request.thread_id}}
    await graph.ainvoke(Command(resume=request.status), config=config)
    return {"message": f"Graph resumed with status: {request.status}"}
    

