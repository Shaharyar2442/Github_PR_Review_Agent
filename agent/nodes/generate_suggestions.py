import asyncio
from typing import Dict, Any, List
from agent.state import AgentState
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import GEMINI_API_KEY

llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite", 
    api_key=GEMINI_API_KEY, 
    temperature=0.4
)



from agent.tools.github_tools import github_search_code, github_read_file
from langgraph.prebuilt import create_react_agent

# ────────────────────────────────────────────────────────────
async def generate_suggestions_node(state: AgentState) -> Dict[str, Any]:
    issues = state["issues"]
    owner = state["owner"]
    repo = state["repo"]
    
    suggestions = []
    
    # Native LangChain tools bound directly to the agent (No MCP overhead!)
    tools = [github_search_code, github_read_file]
    sub_agent = create_react_agent(llm, tools=tools)
    
    # Process issues sequentially to avoid blowing up Render's 512MB RAM
    for issue in issues:
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
                final_text = "\n".join(block.get("text", "") for block in final_message if isinstance(block, dict) and "text" in block)
            else:
                final_text = str(final_message)
                
            suggestions.append(final_text)
        except Exception as e:
            suggestions.append(f"Could not generate suggestion due to error: {e}")

    return {"suggestions": suggestions}
