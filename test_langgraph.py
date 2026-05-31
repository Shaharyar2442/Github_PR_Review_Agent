from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt

class State(TypedDict):
    x: int

def node_a(state: State):
    return {"x": state["x"] + 1}

def node_b(state: State):
    val = interrupt("give me a value")
    return {"x": state["x"] + val}

graph = StateGraph(State)
graph.add_node("a", node_a)
graph.add_node("b", node_b)
graph.add_edge(START, "a")
graph.add_edge("a", "b")
graph.add_edge("b", END)

app = graph.compile(checkpointer=MemorySaver())

config = {"configurable": {"thread_id": "test1"}}
print("Invoking graph...")
res = app.invoke({"x": 1}, config)

snapshot = app.get_state(config)
print("\n--- Snapshot ---")
print(f"Next: {snapshot.next}")
print(f"Tasks: {snapshot.tasks}")
if snapshot.tasks:
    print(f"Interrupts: {snapshot.tasks[0].interrupts}")
