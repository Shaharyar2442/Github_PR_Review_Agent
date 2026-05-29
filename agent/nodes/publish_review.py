from typing import Dict, Any
from agent.state import AgentState

def publish_review_node(state: AgentState) -> Dict[str, Any]:
    print("\n--- PUBLISHING REVIEW ---")
    print("Approval Status:", state.get("approval_status"))
    print("Mocking GitHub PR Comment...")
    print("Successfully posted to GitHub!")
    
    return {}
