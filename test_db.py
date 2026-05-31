import asyncio
import os
import sys

# Ensure imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.graph import get_graph, init_graph, close_graph

async def test_pending():
    await init_graph()
    graph = get_graph()
    
    print("Listing threads from Checkpointer...")
    count = 0
    try:
        # Pass an empty config dict to list all threads safely
        async for thread in graph.checkpointer.alist({"configurable": {}}):
            count += 1
            snapshot = await graph.aget_state(thread.config)
            print(f"Thread: {thread.config}")
            print(f"Next: {snapshot.next}")
            if snapshot.next == ("human_approval",):
                print("=> PENDING HUMAN APPROVAL")
                state = snapshot.values
                print(f"   PR #{state.get('pr_number')} Issues: {len(state.get('issues', []))}")
            else:
                print("=> NOT PENDING")
    except Exception as e:
        print("Error during alist:", e)
    
    print(f"Total threads: {count}")
    await close_graph()

if __name__ == "__main__":
    asyncio.run(test_pending())
