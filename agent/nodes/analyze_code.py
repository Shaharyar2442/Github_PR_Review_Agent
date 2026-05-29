from typing import Dict, Any
from agent.state import AgentState
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import sys
import os
from tenacity import retry,stop_after_attempt,wait_exponential
from agent.search_codebase import search_codebase
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import GEMINI_API_KEY


# Boilerplate: Initialize our LLM (using the free tier Gemini model)
llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite", 
    api_key=GEMINI_API_KEY, 
    temperature=0.2
)



@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def analyze_code_node(state:AgentState)->Dict[str,Any]:
    diff=state["pr_diff"]

    # NEW: Search ChromaDB for related files to give the LLM full context!
    try:
        codebase_context = search_codebase(diff, n_results=3)
    except Exception:
        codebase_context = "No codebase context available."

    prompt=f"""
    You are a Senior AI code reviewer. Your job is to analyze the following pull request diff and provide a detailed review. You should focus on:
    1. Code correctness
    2. Potential bugs
    3. Security vulnerabilities
    4. Best practices
    5. Suggestions for improvement
    6. Breaking changes — check if any modified functions/classes are used in other files!
    
    PR Diff:
    {diff}
    
    Codebase Context (other files in the repo that may be affected):
    {codebase_context}
    
    Please provide your review in the following format:
    1. Overall assessment
    2. Detailed review
    3. Breaking change analysis (based on the codebase context)
    4. Suggestions
    """
    response= llm.invoke([HumanMessage(content=prompt)])
    return {"raw_analysis":response.content}
    
    
