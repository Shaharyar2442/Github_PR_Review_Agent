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
    
    # ─── YOUR TURN ──────────────────────────────────────────────
    # Goal: Pause the graph using `interrupt()`.
    # Hint: 
    # 1. Call `interrupt(review_context)` and store the result in a variable (e.g., `human_response`).
    #    When the graph pauses, it will yield `review_context` to the caller.
    #    When resumed, `interrupt()` will return whatever the human passed back!
    # 2. Return a dictionary updating the state with: `{"approval_status": human_response}`
    # Expected result: The node pauses execution, gets human input, and updates the state.
    # ────────────────────────────────────────────────────────────
    # TODO: Add your interrupt logic here!
    human_response=interrupt(review_context)

    print("Human Response:", human_response) 
    return {"approval_status": human_response}
