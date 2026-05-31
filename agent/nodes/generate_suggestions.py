from typing import Dict, Any
from agent.state import AgentState
from agent.llm import default_llm
from agent.tools.github_tools import github_search_code, github_read_file
from langgraph.prebuilt import create_react_agent
from loguru import logger


async def generate_suggestions_node(state: AgentState) -> Dict[str, Any]:
    issues = state["issues"]
    owner = state["owner"]
    repo = state["repo"]

    suggestions = []

    # Create the ReAct sub-agent ONCE outside the loop (#9)
    # Previously this was recreated per-issue, wasting memory on 512MB Render
    tools = [github_search_code, github_read_file]
    sub_agent = create_react_agent(default_llm, tools=tools)

    # Process issues sequentially to avoid blowing up Render's 512MB RAM
    for i, issue in enumerate(issues):
        logger.info(f"Generating suggestion for issue {i+1}/{len(issues)}")
        prompt = f"""
        You are a senior code reviewer reviewing the repository: {owner}/{repo}.
        You are given a code issue identified in a PR.
        Issue: {issue}
        
        Your job is to provide a concise, highly accurate suggestion to fix it.
        CRITICAL: Use the 'github_search_code' and 'github_read_file' tools to search the {owner}/{repo} repository and understand the context around this issue in the codebase BEFORE answering. Always pass the owner '{owner}' and repo '{repo}' arguments to these tools.
        
        Return ONLY the final string suggestion.
        """

        try:
            result = await sub_agent.ainvoke({"messages": [("user", prompt)]})
            final_message = result["messages"][-1].content

            if isinstance(final_message, list):
                # Gemini sometimes returns a list of blocks
                final_text = "\n".join(
                    block.get("text", "") for block in final_message
                    if isinstance(block, dict) and "text" in block
                )
            else:
                final_text = str(final_message)

            suggestions.append(final_text)
        except Exception as e:
            logger.error(f"Failed to generate suggestion for issue: {issue[:80]}... Error: {e}")
            suggestions.append(f"Could not generate suggestion due to error: {e}")

    return {"suggestions": suggestions}
