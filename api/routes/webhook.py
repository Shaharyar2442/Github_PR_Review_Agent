from starlette import responses
from fastapi import APIRouter, BackgroundTasks, Request
from pydantic import BaseModel
from typing import Dict, Any
from loguru import logger
# We'll import our graph to trigger it!
from agent.graph import graph

router = APIRouter()

# ─── YOUR TURN (PHASE 6) ──────────────────────────────────────
# Goal: Harden our webhook route with structured logging and error handling.
# Hint:
# 1. Import `logger` from `loguru`: `from loguru import logger`
# 2. Replace the basic `print` or empty states with `logger.info(...)`
#    Example: `logger.info(f"Received webhook for PR #{pr_number}")`
# 3. Add a basic `try/except` block inside `run_agent` to catch and log any errors
#    during the LangGraph execution: `logger.error(f"Agent failed: {e}")`
# Expected result: Clean, color-coded logs in your terminal whenever a webhook hits!
# ────────────────────────────────────────────────────────────

# TODO: Add your webhook route here!
@router.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    payload=await request.json()
    action=payload.get("action")
    logger.info(f"Received webhook")

    if action not in ["opened","synchronize"]:
        logger.info("Invalid action, Ignoring")
        return {"message":"Invalid action, Ignoring"}
    pr_number=payload.get("pull_request").get("number")
    logger.info(f"Received webhook for PR #{pr_number}")
    owner=payload.get("repository").get("owner").get("login")
    logger.info(f"Received webhook for PR #{pr_number} by {owner}")
    repo=payload.get("repository").get("name")
    logger.info(f"Received webhook for PR #{pr_number} by {owner} in repo {repo}")

    async def run_agent(owner,repo,pr_number):
        initial_state={
            "owner":owner,
            "repo":repo,
            "pr_number":pr_number
        }
        config={"configurable":{"thread_id":f"pr_{pr_number}"}}
        try:
            await graph.ainvoke(initial_state,config=config)
            logger.info("Webhook received and agent started")
            return responses.JSONResponse({"message":"Webhook received and agent started"})
        except Exception as e:
            logger.error(f"Agent failed: {e}")
            return responses.JSONResponse({"message":"Webhook received but agent failed to start"})

    background_tasks.add_task(run_agent,owner,repo,pr_number)


