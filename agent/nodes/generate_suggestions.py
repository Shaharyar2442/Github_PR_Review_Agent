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

# ─── YOUR TURN ──────────────────────────────────────────────
# Goal: Concurrently ask the LLM for a code suggestion for *each* individual issue.
# Hint: 
# 1. We'll make this function asynchronous: 
#    `async def generate_suggestions_node(state: AgentState) -> Dict[str, Any]:`
# 2. Inside, get the list of `state["issues"]`.
# 3. Write a small helper function inside the node:
#    `async def get_suggestion(issue: str) -> str:`
#    This helper should create a prompt asking for a fix for the specific `issue` and 
#    use `await llm.ainvoke([HumanMessage(content=prompt)])` to call the LLM asynchronously.
# 4. Use `asyncio.gather(*[get_suggestion(i) for i in state["issues"]])` to run all 
#    those helper functions at exactly the same time!
# 5. Return a dictionary mapping "suggestions" to the resulting list of strings.
# Expected result: An async node that fetches multiple suggestions concurrently, saving a ton of time!

# ────────────────────────────────────────────────────────────
async def generate_suggestions_node(state: AgentState) -> Dict[str, Any]:
    issues=state["issues"]
    async def get_suggestion(issue:str):
        prompt=f"""
        You are a senior code reviewer. You are given a code issue and you must provide a concise suggestion to fix it.

        Example:
        Issue: Variable 'total' might be referenced before assignment.
        Suggestion: Initialize 'total' before the conditional blocks to ensure it is always defined before use.

        Now analyze the following issue:
        Issue: {issue}

        Return only the suggestion.
        """
        message=await llm.ainvoke([HumanMessage(content=prompt)])
        return message.content
    
    suggestions=await asyncio.gather(*[get_suggestion(i)for i in issues])
    return {"suggestions":suggestions}
