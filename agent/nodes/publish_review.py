from typing import Dict, Any
from agent.state import AgentState
from agent.utils.github_api import async_post_pr_review
from loguru import logger


async def publish_review_node(state: AgentState) -> Dict[str, Any]:
    """Post the final AI review back to the GitHub PR using async HTTP."""
    logger.info("--- PUBLISHING REVIEW ---")
    owner = state["owner"]
    repo = state["repo"]
    pr_number = state["pr_number"]
    issues = state.get("issues", [])
    suggestions = state.get("suggestions", [])

    body = "## 🤖 AI Code Review\n\n### ⚠️ Issues Found:\n"
    for issue in issues:
        body += f"- {issue}\n"
    body += "\n### 💡 Suggestions:\n"
    for sug in suggestions:
        body += f"- {sug}\n"

    logger.info(f"Posting review to {owner}/{repo} PR #{pr_number}...")
    try:
        await async_post_pr_review(owner, repo, pr_number, body)
        logger.info("Successfully posted review.")
    except Exception as e:
        logger.error(f"FAILED TO POST REVIEW to {owner}/{repo}#{pr_number}: {e}")
    return {}
