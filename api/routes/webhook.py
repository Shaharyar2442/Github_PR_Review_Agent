from starlette import responses
from fastapi import APIRouter, BackgroundTasks, Request
from pydantic import BaseModel
from typing import Dict, Any
from loguru import logger
from agent.graph import get_graph
import hmac
import hashlib
from fastapi import APIRouter, HTTPException
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import GITHUB_WEBHOOK_SECRET

router = APIRouter()

@router.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    body = await request.body()
    signature = request.headers.get("x-hub-signature-256")
    
    # Verify GitHub App Webhook Signature
    if GITHUB_WEBHOOK_SECRET and signature:
        mac = hmac.new(GITHUB_WEBHOOK_SECRET.encode(), msg=body, digestmod=hashlib.sha256)
        expected_signature = "sha256=" + mac.hexdigest()
        if not hmac.compare_digest(expected_signature, signature):
            logger.warning("Invalid GitHub webhook signature")
            raise HTTPException(status_code=401, detail="Invalid signature")

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
            graph = get_graph()
            await graph.ainvoke(initial_state,config=config)
            logger.info("Webhook received and agent started")
            return responses.JSONResponse({"message":"Webhook received and agent started"})
        except Exception as e:
            logger.exception("Agent failed:")
            return responses.JSONResponse({"message":"Webhook received but agent failed to start"})

    background_tasks.add_task(run_agent,owner,repo,pr_number)


