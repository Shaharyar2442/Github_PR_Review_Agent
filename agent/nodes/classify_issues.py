import time
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from loguru import logger
from agent.state import AgentState
from agent.llm import get_structured_llm
from langchain_core.messages import HumanMessage


# ────────────────────────────────────────────────────────────
class IssueList(BaseModel):
    issues: List[str] = Field(description="List of issues found in the code")


def classify_issues_node(state: AgentState) -> Dict[str, Any]:
    start_time = time.time()
    owner = state.get("owner", "unknown")
    repo = state.get("repo", "unknown")
    pr_number = state.get("pr_number", "unknown")
    
    logger.info(f"[{owner}/{repo}#{pr_number}] Starting classify_issues_node...")
    
    llm_with_schema = get_structured_llm(IssueList)
    prompt = f""" You are a senior code reviewer. Analyze the following raw analysis from a code review and extract all the issues and potential bugs into a structured list.
    Raw Analysis:{state['raw_analysis']}
    
    Return ONLY a list of issues.
    """
    
    logger.info(f"[{owner}/{repo}#{pr_number}] Invoking structured LLM to classify issues...")
    llm_start = time.time()
    response = llm_with_schema.invoke([HumanMessage(content=prompt)])
    logger.info(f"[{owner}/{repo}#{pr_number}] Structured classification completed in {time.time() - llm_start:.2f}s (Found {len(response.issues)} issues)")
    
    logger.info(f"[{owner}/{repo}#{pr_number}] classify_issues_node completed in {time.time() - start_time:.2f}s total")
    
    return {"issues": response.issues}
