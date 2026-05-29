from typing import Dict, Any, List
from pydantic import BaseModel, Field
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
    temperature=0.0
)


# ────────────────────────────────────────────────────────────
class IssueList(BaseModel):
    issues:List[str]=Field(description="List of issues found in the code")






def classify_issues_node(state:AgentState)->Dict[str,Any]:
    structured_llm=llm.with_structured_output(IssueList)
    prompt=f""" You are a senior code reviewer. Analyze the following raw analysis from a code review and extract all the issues and potential bugs into a structured list.
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
    response=structured_llm.invoke([HumanMessage(content=prompt)])
    return {"issues":response.issues}
