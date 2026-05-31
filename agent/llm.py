"""
Shared LLM instances for the agent pipeline.

Instead of each node creating its own ChatGoogleGenerativeAI client
(each with its own HTTP connection pool and internal buffers), we
share instances here to reduce memory footprint on the 512MB Render tier.
"""

from langchain_openai import ChatOpenAI
from config import OPENROUTER_API_KEY

# OpenRouter uses the OpenAI API standard
# We use the free gemini-2.0-flash-lite model available on OpenRouter
default_llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    model="moonshotai/kimi-k2.6:free",
    temperature=0.2,
)

structured_llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    model="moonshotai/kimi-k2.6:free",
    temperature=0.0,
)
