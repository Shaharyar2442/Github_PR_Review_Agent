from typing import Dict, Any
from agent.state import AgentState
from github_mcp.server import get_pr_metadata, get_pr_diff

# ─── YOUR TURN ──────────────────────────────────────────────
# Goal: Build the first LangGraph node that fetches PR data.
# Hint: A LangGraph node is just a normal Python function that takes the current `state`
#       (of type `AgentState`) as input, and returns a dictionary containing ONLY 
#       the fields it wants to update or add to the state.
#       Inside this function:
#       1. Extract `owner`, `repo`, and `pr_number` from the state.
#       2. Call your MCP tools `get_pr_metadata` and `get_pr_diff`.
#       3. Return a dictionary mapping "pr_metadata" and "pr_diff" to the results.
# Expected result: A function `fetch_pr_node(state: AgentState) -> Dict[str, Any]`
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