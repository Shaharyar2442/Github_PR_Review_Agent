from typing import Dict, Any, List
from pydantic import BaseModel, Field
from agent.state import AgentState
from agent.llm import get_structured_llm
from langchain_core.messages import HumanMessage


# ────────────────────────────────────────────────────────────
class IssueList(BaseModel):
    issues: List[str] = Field(description="List of issues found in the code")


def classify_issues_node(state: AgentState) -> Dict[str, Any]:
    llm_with_schema = get_structured_llm(IssueList)
    prompt = f""" You are a senior code reviewer. Analyze the following raw analysis from a code review and extract all the issues and potential bugs into a structured list.
    Raw Analysis:{state['raw_analysis']}
    
    Return the issues in the following format:
    {{
        "issues": [
            "issue 1",
            "issue 2",
            "issue 3"
        ]
    }} 
    """
    response = llm_with_schema.invoke([HumanMessage(content=prompt)])
    return {"issues": response.issues}
