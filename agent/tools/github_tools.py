import httpx
import base64
from langchain_core.tools import tool
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from agent.utils.github_api import get_github_headers

@tool
def github_search_code(owner: str, repo: str, query: str) -> str:
    """
    Search the target GitHub repository for code matching the given query.
    Use this to find relevant files when you need more context outside of the PR diff.
    """
    url = f"https://api.github.com/search/code?q={query}+repo:{owner}/{repo}"
    try:
        response = httpx.get(url, headers=get_github_headers(owner, repo))
        response.raise_for_status()
        
        data = response.json()
        items = data.get("items", [])
        
        if not items:
            return "No matching files found in the repository."
            
        results = []
        for item in items[:5]: # Return top 5 results
            results.append(f"File: {item['path']}")
            
        return "Found the following relevant files:\n" + "\n".join(results) + "\n\nUse github_read_file to view their contents if needed."
        
    except Exception as e:
        return f"Error searching codebase: {e}"

@tool
def github_read_file(owner: str, repo: str, file_path: str, start_line: int = 1, end_line: int = -1) -> str:
    """
    Read the contents of a specific file from the target GitHub repository.
    Use start_line and end_line to specify a range of lines to read, or leave end_line as -1 to read to the end.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
    try:
        response = httpx.get(url, headers=get_github_headers(owner, repo))
        response.raise_for_status()
        
        data = response.json()
        if "content" not in data:
            return "Error: File content not found or file is too large."
            
        # GitHub returns base64 encoded content
        content = base64.b64decode(data["content"]).decode("utf-8")
        lines = content.split("\n")
        
        if end_line == -1:
            end_line = len(lines)
            
        start_idx = max(0, start_line - 1)
        end_idx = min(len(lines), end_line)
        
        output = f"--- {file_path} (lines {start_line}-{end_idx}) ---\n"
        for i, line in enumerate(lines[start_idx:end_idx]):
            output += f"{start_idx + i + 1}: {line}\n"
            
        return output
        
    except Exception as e:
        return f"Error reading file {file_path}: {e}"
