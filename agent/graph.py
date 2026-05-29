from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from agent.state import AgentState

from agent.nodes.fetch_pr import fetch_pr_node
from agent.nodes.analyze_code import analyze_code_node
from agent.nodes.classify_issues import classify_issues_node
from agent.nodes.generate_suggestions import generate_suggestions_node
from agent.nodes.human_approval import human_approval_node
from agent.nodes.publish_review import publish_review_node



memory=MemorySaver()
builder = StateGraph(AgentState)
builder.add_node("fetch", fetch_pr_node)
builder.add_node("analyze", analyze_code_node)
builder.add_node("classify", classify_issues_node)
builder.add_node("suggest", generate_suggestions_node)
builder.add_node("human_approval", human_approval_node)
builder.add_node("publish", publish_review_node)

builder.set_entry_point("fetch")
builder.add_edge("fetch", "analyze")
builder.add_edge("analyze", "classify")
builder.add_edge("classify", "suggest")
builder.add_edge("suggest","human_approval")

def route_after_approval(state: AgentState):
    if state.get("approval_status") == "approved":
        return "publish"
    return END
builder.add_conditional_edges("human_approval", route_after_approval)
builder.add_edge("publish", END)

graph = builder.compile(checkpointer=memory)


if __name__ == "__main__":
    import asyncio
    
    async def run_test():
        initial_state = {
            "owner": "Shaharyar2442",
            "repo": "Github_PR_Review_Agent",
            "pr_number": 2
        }
        
        config = {"configurable": {"thread_id": "test_pr_1"}}
        
        print("\n=== RUN 1: Starting Graph ===")
        await graph.ainvoke(initial_state, config=config)
        
        print("\n=== RUN 2: Resuming Graph ===")
        await graph.ainvoke(Command(resume="approved"), config=config)
        
        print("\n--- Done! ---")

    asyncio.run(run_test())
