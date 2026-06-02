import time
from typing import Dict, Any
from loguru import logger
from agent.state import AgentState
from agent.utils.github_api import async_get_pr_metadata, async_get_pr_diff


async def fetch_pr_node(state: AgentState) -> Dict[str, Any]:
    """Fetch PR metadata and diff from GitHub using async HTTP calls."""
    start_time = time.time()
    owner = state['owner']
    repo = state['repo']
    pr_number = state['pr_number']
    
    logger.info(f"[{owner}/{repo}#{pr_number}] Starting fetch_pr_node...")
    
    meta_start = time.time()
    pr_metadata = await async_get_pr_metadata(owner, repo, pr_number)
    logger.info(f"[{owner}/{repo}#{pr_number}] Fetched PR metadata in {time.time() - meta_start:.2f}s")
    
    diff_start = time.time()
    pr_diff = await async_get_pr_diff(owner, repo, pr_number)
    logger.info(f"[{owner}/{repo}#{pr_number}] Fetched PR diff in {time.time() - diff_start:.2f}s (Diff length: {len(pr_diff)} chars)")
    
    logger.info(f"[{owner}/{repo}#{pr_number}] fetch_pr_node completed in {time.time() - start_time:.2f}s total")
    
    return {
        "pr_metadata": pr_metadata,
        "pr_diff": pr_diff
    }