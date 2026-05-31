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



from agent.mcp_client import get_server_params, create_langchain_tools
from mcp.client.stdio import stdio_client
from mcp import ClientSession
from langgraph.prebuilt import create_react_agent

# ────────────────────────────────────────────────────────────
async def generate_suggestions_node(state: AgentState) -> Dict[str, Any]:
    issues = state["issues"]
    
    # Fix OOM: We spawn the MCP connection ONCE for all issues, 
    # instead of N concurrent subprocesses.
    suggestions = []
    
    async with stdio_client(get_server_params()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await create_langchain_tools(session)
            
            # Filter to only the tools we want the sub-agent to use
            allowed_tools = [t for t in tools if t.name in ["search_codebase_tool", "read_file_tool", "get_pr_diff"]]
            sub_agent = create_react_agent(llm, tools=allowed_tools)
            
            # Process issues sequentially to avoid blowing up Render's 512MB RAM
            for issue in issues:
                prompt = f"""
                You are a senior code reviewer. You are given a code issue identified in a PR.
                Issue: {issue}
                
                Your job is to provide a concise, highly accurate suggestion to fix it.
                CRITICAL: Use the 'search_codebase_tool' and 'read_file_tool' to understand the context around this issue in the codebase BEFORE answering.
                
                Return ONLY the final string suggestion.
                """
                
                try:
                    result = await sub_agent.ainvoke({"messages": [("user", prompt)]})
                    final_message = result["messages"][-1].content
                    suggestions.append(final_message)
                except Exception as e:
                    suggestions.append(f"Could not generate suggestion due to error: {e}")

    return {"suggestions": suggestions}
