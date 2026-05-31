from fastapi import APIRouter, BackgroundTasks, Request, HTTPException
from loguru import logger
from agent.graph import get_graph
import hmac
import hashlib

from config import GITHUB_WEBHOOK_SECRET

router = APIRouter()


@router.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    body = await request.body()

    # Verify GitHub App Webhook Signature (#3)
    # Verification is MANDATORY when a secret is configured — cannot be skipped
    # by omitting the signature header.
    if GITHUB_WEBHOOK_SECRET:
        signature = request.headers.get("x-hub-signature-256")
        if not signature:
            logger.warning("Webhook received without signature header — rejecting")
            raise HTTPException(status_code=401, detail="Missing signature header")
        mac = hmac.new(GITHUB_WEBHOOK_SECRET.encode(), msg=body, digestmod=hashlib.sha256)
        expected_signature = "sha256=" + mac.hexdigest()
        if not hmac.compare_digest(expected_signature, signature):
            logger.warning("Invalid GitHub webhook signature — rejecting")
            raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()
    action = payload.get("action")
    logger.info(f"Received webhook with action: {action}")

    if action not in ["opened", "synchronize"]:
        logger.info(f"Ignoring webhook action: {action}")
        return {"message": "Ignored — not a PR open/sync event"}

    # Safely extract payload fields with validation (#17)
    pr_data = payload.get("pull_request")
    repo_data = payload.get("repository")
    if not pr_data or not repo_data:
        logger.warning("Malformed webhook payload: missing pull_request or repository")
        raise HTTPException(status_code=400, detail="Malformed webhook payload")

    pr_number = pr_data["number"]
    owner = repo_data["owner"]["login"]
    repo = repo_data["name"]
    logger.info(f"Processing webhook for {owner}/{repo} PR #{pr_number}")

    async def run_agent(owner: str, repo: str, pr_number: int):
        """Background task to run the full agent pipeline."""
        initial_state = {
            "owner": owner,
            "repo": repo,
            "pr_number": pr_number
        }
        # Globally unique thread ID to prevent cross-tenant collisions (#16)
        config = {"configurable": {"thread_id": f"pr-{owner}-{repo}-{pr_number}"}}
        try:
            graph = get_graph()
            await graph.ainvoke(initial_state, config=config)
            logger.info(f"Agent completed for {owner}/{repo}#{pr_number}")
        except Exception as e:
            logger.exception(f"Agent pipeline failed for {owner}/{repo}#{pr_number}")
            # TODO: Consider posting a "review failed" comment to the PR

    background_tasks.add_task(run_agent, owner, repo, pr_number)
    return {"message": f"Webhook received — agent started for {owner}/{repo}#{pr_number}"}
