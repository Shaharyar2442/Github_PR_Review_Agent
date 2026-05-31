import asyncio
from agent.nodes.generate_suggestions import generate_suggestions_node

async def test():
    state = {
        "owner": "Shaharyar2442",
        "repo": "Github_PR_Review_Agent",
        "issues": ["In generate_suggestions.py, we need to pass the owner and repo to github_search_code."],
        "pr_number": 1
    }
    res = await generate_suggestions_node(state)
    print(res)

if __name__ == "__main__":
    import sys
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test())
