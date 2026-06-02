import time
from typing import Dict, Any
from agent.state import AgentState
from agent.llm import default_llm
from langchain_core.messages import HumanMessage
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger

# Max diff characters to send to the LLM to prevent OOM on huge PRs (#21)
MAX_DIFF_CHARS = 30_000  # ~7500 tokens, well within flash-lite's context


@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=2, min=5, max=60))
def analyze_code_node(state: AgentState) -> Dict[str, Any]:
    start_time = time.time()
    diff = state["pr_diff"]
    owner = state.get("owner", "unknown")
    repo = state.get("repo", "unknown")
    pr_number = state.get("pr_number", "unknown")
    
    logger.info(f"[{owner}/{repo}#{pr_number}] Starting analyze_code_node...")

    # Guard against massive diffs that could spike memory or exceed context (#21)
    if len(diff) > MAX_DIFF_CHARS:
        logger.warning(f"[{owner}/{repo}#{pr_number}] PR diff is {len(diff)} chars, truncating to {MAX_DIFF_CHARS}")
        diff = diff[:MAX_DIFF_CHARS] + "\n\n[... diff truncated for analysis — only the first portion was reviewed ...]"

    prompt = f"""
    You are a Senior AI code reviewer. Your job is to analyze the following pull request diff and provide a detailed review. You should focus on:
    1. Code correctness
    2. Potential bugs
    3. Security vulnerabilities
    4. Best practices
    5. Suggestions for improvement
    
    IMPORTANT CRITERIA:
    - Pay extremely close attention to the `+` and `-` symbols at the start of each line in the diff.
    - Lines starting with `+` are NEW code being ADDED by the developer. This is where you should look for bugs.
    - Lines starting with `-` are OLD code being REMOVED by the developer. Do NOT flag bugs or security vulnerabilities on code that is being removed, because the developer is already deleting it!

    
    PR Diff:
    {diff}
    
    Please provide your review in the following format:
    1. Overall assessment
    2. Detailed review
    3. Suggestions
    """
    
    logger.info(f"[{owner}/{repo}#{pr_number}] Invoking LLM for initial analysis...")
    llm_start = time.time()
    response = default_llm.invoke([HumanMessage(content=prompt)])
    logger.info(f"[{owner}/{repo}#{pr_number}] LLM analysis completed in {time.time() - llm_start:.2f}s")
    
    logger.info(f"[{owner}/{repo}#{pr_number}] analyze_code_node completed in {time.time() - start_time:.2f}s total")
    
    return {"raw_analysis": response.content}
