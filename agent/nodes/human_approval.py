from typing import Dict, Any
from langgraph.types import interrupt
from agent.state import AgentState

def human_approval_node(state: AgentState) -> Dict[str, Any]:
    print("\n--- HUMAN IN THE LOOP ---")
    print("Agent is pausing to ask for human approval before publishing.")
    
    # We provide the extracted issues and suggestions to the human so they can review them
    review_context = {
        "issues": state.get("issues", []),
        "suggestions": state.get("suggestions", [])
    }
    
    
    human_response=interrupt(review_context)

    print("Human Response:", human_response) 
    return {"approval_status": human_response}
