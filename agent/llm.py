"""
Shared LLM instances for the agent pipeline with Fallbacks.

We use Gemini as the primary LLM because its free tier offers 1,000,000 TPM
(Tokens Per Minute), which easily handles massive 30,000-character PR diffs.

If Gemini hits a rate limit or goes down, it automatically falls back to Groq.
"""

from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.callbacks import BaseCallbackHandler
from loguru import logger
from typing import Any
from config import GROQ_API_KEY, GEMINI_API_KEY

class FallbackLogger(BaseCallbackHandler):
    def on_llm_error(self, error: BaseException, **kwargs: Any) -> Any:
        logger.warning(f"LLM Error encountered (fallback may trigger): {error}")

_gemini = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    api_key=GEMINI_API_KEY,
    temperature=0.2,
    callbacks=[FallbackLogger()]
)

_groq = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama-3.3-70b-versatile",
    temperature=0.2,
)

# Expose the default LLM (for basic generation)
default_llm = _gemini.with_fallbacks([_groq])

def get_react_agent_llm(tools):
    """
    Returns an LLM with tools bound, ensuring the fallback mechanism
    applies to both the primary and fallback LLMs safely.
    """
    gemini_bound = _gemini.bind_tools(tools)
    groq_bound = _groq.bind_tools(tools)
    return gemini_bound.with_fallbacks([groq_bound])

def get_structured_llm(schema):
    """
    Returns an LLM bound to a specific Pydantic schema for structured output,
    with the fallback mechanism intact.
    """
    # Create fresh instances with temperature 0.0 for deterministic structured output
    gemini_struct = ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite",
        api_key=GEMINI_API_KEY,
        temperature=0.0,
        callbacks=[FallbackLogger()]
    ).with_structured_output(schema)
    
    groq_struct = ChatGroq(
        api_key=GROQ_API_KEY,
        model="llama-3.3-70b-versatile",
        temperature=0.0,
    ).with_structured_output(schema)
    
    # Apply fallback AFTER the structured output wrapper is applied to both
    return gemini_struct.with_fallbacks([groq_struct])
