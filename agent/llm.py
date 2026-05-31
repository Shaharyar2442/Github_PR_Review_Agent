"""
Shared LLM instances for the agent pipeline.

Instead of each node creating its own ChatGoogleGenerativeAI client
(each with its own HTTP connection pool and internal buffers), we
share instances here to reduce memory footprint on the 512MB Render tier.
"""

from langchain_groq import ChatGroq
from config import GROQ_API_KEY

# Groq provides extremely fast inference and a generous free tier
default_llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama-3.3-70b-versatile",
    temperature=0.2,
)

structured_llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama-3.3-70b-versatile",
    temperature=0.0,
)
