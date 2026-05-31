import asyncio
import sys
import os
from agent.graph import get_graph, init_graph, close_graph
from langgraph.types import Command

async def main():
    await init_graph()
    graph = get_graph()
    
    threads_generator = graph.checkpointer.alist({"configurable": {}})
    unique_thread_ids = set()
    async for t in threads_generator:
        tid = t.config.get("configurable", {}).get("thread_id")
        if tid:
            unique_thread_ids.add(tid)
            
    print(f"Unique Thread IDs: {unique_thread_ids}")
    
    for tid in unique_thread_ids:
        snapshot = await graph.aget_state({"configurable": {"thread_id": tid}})
        print(f"\n--- Thread: {tid} ---")
        print(f"Next: {snapshot.next}")
        print(f"Tasks: {snapshot.tasks}")
        if snapshot.tasks and len(snapshot.tasks) > 0:
            print(f"Interrupts: {snapshot.tasks[0].interrupts}")

    await close_graph()

if __name__ == "__main__":
    if sys.platform == 'win32':
        import selectors
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
