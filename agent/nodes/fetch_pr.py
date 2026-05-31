from typing import Dict, Any
from agent.state import AgentState
from agent.utils.github_api import get_pr_metadata, get_pr_diff

# ────────────────────────────────────────────────────────────
def fetch_pr_node(state: AgentState) -> Dict[str, Any]:
    owner=state['owner']
    repo=state['repo']
    pr_number=state['pr_number']
    pr_metadata=get_pr_metadata(owner,repo,pr_number)
    pr_diff=get_pr_diff(owner,repo,pr_number)
    return {
        "pr_metadata":pr_metadata,
        "pr_diff":pr_diff
    }