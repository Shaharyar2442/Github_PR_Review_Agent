from typing import TypedDict, Dict, Any

# ─── YOUR TURN ──────────────────────────────────────────────
# Goal: Define the state that will be passed between our LangGraph nodes.
# Hint: Create a class named `AgentState` that inherits from `TypedDict`. 
#       We need fields to store the following data as it flows through the graph:
#       - The PR input: owner (str), repo (str), pr_number (int)
#       - The fetched data: pr_metadata (Dict[str, Any]), pr_diff (str)
#       - The LLM analysis result: raw_analysis (str)
# Expected result: A TypedDict class containing those 6 fields with their types.
# ────────────────────────────────────────────────────────────
class AgentState(TypedDict):
    owner:str
    repo:str
    pr_number:int
    pr_metadata:Dict[str,Any] 
    pr_diff:str
    raw_analysis:str
    issues:list[str]
    suggestions:list[str]
    approval_status:str
    

