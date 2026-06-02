import time
from typing import Dict, Any
from agent.state import AgentState
from agent.llm import get_react_agent_llm
from agent.tools.github_tools import github_search_code, github_read_file
from langgraph.prebuilt import create_react_agent
from loguru import logger

async def generate_suggestions_node(state: AgentState) -> Dict[str, Any]:
    start_time = time.time()
    issues = state["issues"]
    owner = state["owner"]
    repo = state["repo"]
    pr_number = state.get("pr_number", "unknown")
    
    logger.info(f"[{owner}/{repo}#{pr_number}] Starting generate_suggestions_node for {len(issues)} issues...")

    suggestions = []

    from langchain_core.tools import tool

    head_sha = state.get("pr_metadata", {}).get("head", {}).get("sha", "")

    @tool
    def search_repo_code(query: str) -> str:
        """Search the target GitHub repository for code matching the given query."""
        tool_start = time.time()
        res = github_search_code.invoke({"owner": owner, "repo": repo, "query": query})
        logger.debug(f"[{owner}/{repo}#{pr_number}] Tool 'search_repo_code' executed in {time.time() - tool_start:.2f}s")
        return res

    @tool
    def read_repo_file(file_path: str, start_line: int = 1, end_line: int = -1) -> str:
        """Read the contents of a specific file from the target GitHub repository."""
        tool_start = time.time()
        res = github_read_file.invoke({
            "owner": owner, 
            "repo": repo, 
            "file_path": file_path, 
            "start_line": start_line, 
            "end_line": end_line, 
            "ref": head_sha
        })
        logger.debug(f"[{owner}/{repo}#{pr_number}] Tool 'read_repo_file' executed in {time.time() - tool_start:.2f}s")
        return res

    tools = [search_repo_code, read_repo_file]
    react_llm = get_react_agent_llm(tools)
    sub_agent = create_react_agent(react_llm, tools=tools)

    # Process issues sequentially to avoid blowing up Render's 512MB RAM
    for i, issue in enumerate(issues):
        issue_start = time.time()
        logger.info(f"[{owner}/{repo}#{pr_number}] Generating suggestion for issue {i+1}/{len(issues)}")
        prompt = f"""
        You are a senior code reviewer reviewing the repository: {owner}/{repo}.
        You are given a code issue identified in a Pull Request.
        Issue: {issue}
        
        Your job is to provide a concise, highly accurate suggestion to fix it.
        CRITICAL: Use the 'search_repo_code' and 'read_repo_file' tools to search the repository and understand the context around this issue in the codebase BEFORE answering.
        
        Return ONLY the final string suggestion.
        """

        try:
            # Let's log exactly what model is running the React agent
            logger.info(f"[{owner}/{repo}#{pr_number}] Invoking sub_agent for issue {i+1}...")
            agent_start = time.time()
            result = await sub_agent.ainvoke({"messages": [("user", prompt)]})
            logger.info(f"[{owner}/{repo}#{pr_number}] sub_agent.ainvoke completed in {time.time() - agent_start:.2f}s")
            
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
            logger.info(f"[{owner}/{repo}#{pr_number}] Finished suggestion {i+1}/{len(issues)} in {time.time() - issue_start:.2f}s")
        except Exception as e:
            logger.error(f"[{owner}/{repo}#{pr_number}] Failed suggestion for issue {i+1}: {e}")
            suggestions.append(f"Could not generate suggestion due to error: {e}")

    logger.info(f"[{owner}/{repo}#{pr_number}] generate_suggestions_node completed all issues in {time.time() - start_time:.2f}s total")
    return {"suggestions": suggestions}
