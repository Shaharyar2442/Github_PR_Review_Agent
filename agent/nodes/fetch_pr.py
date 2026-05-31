from typing import Dict, Any
from agent.state import AgentState
from agent.utils.github_api import async_get_pr_metadata, async_get_pr_diff


async def fetch_pr_node(state: AgentState) -> Dict[str, Any]:
    """Fetch PR metadata and diff from GitHub using async HTTP calls."""
    owner = state['owner']
    repo = state['repo']
    pr_number = state['pr_number']
    pr_metadata = await async_get_pr_metadata(owner, repo, pr_number)
    pr_diff = await async_get_pr_diff(owner, repo, pr_number)
    return {
        "pr_metadata": pr_metadata,
        "pr_diff": pr_diff
    }