from typing import Dict, Any
from agent.state import AgentState
from agent.utils.github_api import post_pr_review
def publish_review_node(state: AgentState) -> Dict[str, Any]:
    print("\n--- PUBLISHING REVIEW ---")
    owner=state["owner"]
    repo=state["repo"]
    pr_number=state["pr_number"]
    issues=state.get("issues",[])
    suggestions=state.get("suggestions",[])
    body="AI Code Review\n\n ***Issues Found:***\n"
    for issue in issues:
        body+=f" -{issue}\n"
    body+="\n ***Suggestions:***\n"
    for sug in suggestions:
        body += f"- {sug}\n"    
    print(f"Posting real comment to {owner}/{repo} PR #{pr_number}...")
    try:   
        response=post_pr_review(owner,repo,pr_number,body)
        print(f"Posted review response.")
    except Exception as e:   
        print("FAILED TO POST REVIEW",e)
    return {}
