"""
Native LangChain tools for the ReAct sub-agent.
Uses lightweight httpx calls to GitHub REST API — no MCP or vector DB overhead.
"""

import httpx
import base64
from langchain_core.tools import tool
from loguru import logger

from agent.utils.github_api import get_github_headers, _check_rate_limit, GitHubRateLimitError

# Guard: max lines to return to the LLM to avoid token/memory waste
MAX_LINES_TO_RETURN = 500


@tool
def github_search_code(owner: str, repo: str, query: str) -> str:
    """
    Search the target GitHub repository for code matching the given query.
    Use this to find relevant files when you need more context outside of the PR diff.
    """
    url = f"https://api.github.com/search/code?q={query}+repo:{owner}/{repo}"
    try:
        response = httpx.get(url, headers=get_github_headers(owner, repo), timeout=15)
        _check_rate_limit(response)
        response.raise_for_status()

        data = response.json()
        items = data.get("items", [])

        if not items:
            return "No matching files found in the repository."

        results = []
        for item in items[:5]:  # Return top 5 results
            results.append(f"File: {item['path']}")

        return "Found the following relevant files:\n" + "\n".join(results) + "\n\nUse github_read_file to view their contents if needed."

    except GitHubRateLimitError as e:
        return f"GitHub API rate limit reached. Please wait {e.retry_after}s before retrying."
    except Exception as e:
        logger.error(f"Error searching codebase for '{query}' in {owner}/{repo}: {e}")
        return f"Error searching codebase: {e}"


@tool
def github_read_file(owner: str, repo: str, file_path: str, start_line: int = 1, end_line: int = -1, ref: str = None) -> str:
    """
    Read the contents of a specific file from the target GitHub repository.
    Use start_line and end_line to specify a range of lines to read, or leave end_line as -1 to read to the end.
    The 'ref' parameter should be the PR's head commit SHA to read the code exactly as it exists in the Pull Request.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
    if ref:
        url += f"?ref={ref}"
    try:
        response = httpx.get(url, headers=get_github_headers(owner, repo), timeout=15)
        _check_rate_limit(response)
        response.raise_for_status()

        data = response.json()
        if "content" not in data:
            size_bytes = data.get("size", "unknown")
            return f"Error: File content not found. File may be too large ({size_bytes} bytes). GitHub API only returns files up to 1MB via this endpoint."

        # GitHub returns base64 encoded content
        content = base64.b64decode(data["content"]).decode("utf-8")
        lines = content.split("\n")

        if end_line == -1:
            end_line = len(lines)

        start_idx = max(0, start_line - 1)
        end_idx = min(len(lines), end_line)

        # Truncation guard: don't send huge files to the LLM
        requested_lines = end_idx - start_idx
        if requested_lines > MAX_LINES_TO_RETURN:
            end_idx = start_idx + MAX_LINES_TO_RETURN
            truncated = True
        else:
            truncated = False

        output = f"--- {file_path} (lines {start_idx + 1}-{end_idx}) ---\n"
        for i, line in enumerate(lines[start_idx:end_idx]):
            output += f"{start_idx + i + 1}: {line}\n"

        if truncated:
            output += f"\n[... truncated at {MAX_LINES_TO_RETURN} lines. File has {len(lines)} total lines. Use start_line/end_line to read specific sections. ...]"

        return output

    except GitHubRateLimitError as e:
        return f"GitHub API rate limit reached. Please wait {e.retry_after}s before retrying."
    except Exception as e:
        logger.error(f"Error reading file {file_path} from {owner}/{repo}: {e}")
        return f"Error reading file {file_path}: {e}"
