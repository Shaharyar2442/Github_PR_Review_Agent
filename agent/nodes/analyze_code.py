from typing import Dict, Any
from agent.state import AgentState
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import GEMINI_API_KEY


# Boilerplate: Initialize our LLM (using the free tier Gemini model)
llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite", 
    api_key=GEMINI_API_KEY, 
    temperature=0.2
)

# ─── YOUR TURN ──────────────────────────────────────────────
# Goal: Build the second LangGraph node that analyzes the PR diff.
# Hint: Create a function `analyze_code_node(state: AgentState) -> Dict[str, Any]`.
#       Inside it:

#       1. Create a prompt string that asks the LLM to analyze the `state["pr_diff"]`.
#       2. Call the LLM using: `response = llm.invoke([HumanMessage(content=prompt)])`
#       3. Return a dictionary mapping "raw_analysis" to `response.content`.
# Expected result: A function that uses Gemini to analyze the diff and returns the text.
# ────────────────────────────────────────────────────────────
def analyze_code_node(state:AgentState)->Dict[str,Any]:
    diff=state["pr_diff"]
    prompt=f"""
    You are a Senior AI code reviewer. Your job is to analyze the following pull request diff and provide a detailed review. You should focus on:
    1. Code correctness
    2. Potential bugs
    3. Security vulnerabilities
    4. Best practices
    5. Suggestions for improvement
    
    PR Diff:
    {diff}
    
    Please provide your review in the following format:
    1. Overall assessment
    2. Detailed review
    3. Suggestions
    """
    response= llm.invoke([HumanMessage(content=prompt)])
    return {"raw_analysis":response.content}
    
    
