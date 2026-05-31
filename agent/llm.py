"""
Shared LLM instances for the agent pipeline.

Instead of each node creating its own ChatGoogleGenerativeAI client
(each with its own HTTP connection pool and internal buffers), we
share instances here to reduce memory footprint on the 512MB Render tier.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from config import GEMINI_API_KEY

# Used by analyze_code and generate_suggestions (needs some creativity)
default_llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    api_key=GEMINI_API_KEY,
    temperature=0.2,
)

# Used by classify_issues (needs deterministic structured output)
structured_llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    api_key=GEMINI_API_KEY,
    temperature=0.0,
)
