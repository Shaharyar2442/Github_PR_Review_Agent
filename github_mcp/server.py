import httpx
from fastmcp import FastMCP
import sys
import os
import time
import jwt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GITHUB_TOKEN, GITHUB_APP_ID, GITHUB_PRIVATE_KEY

# Initialize the FastMCP server
mcp = FastMCP("GitHub-Review-Agent")

def get_github_headers(owner: str = None, repo: str = None):
    """
    Returns the appropriate GitHub headers. If App ID and Private Key are present,
    it dynamically generates an installation token for the specified repo.
    Otherwise, it falls back to the personal GITHUB_TOKEN.
    """
    if GITHUB_APP_ID and GITHUB_PRIVATE_KEY and owner and repo:
        # 1. Generate JWT for the GitHub App
        now = int(time.time())
        payload = {
            "iat": now - 60,
            "exp": now + (10 * 60),
            "iss": GITHUB_APP_ID
        }
        encoded_jwt = jwt.encode(payload, GITHUB_PRIVATE_KEY, algorithm="RS256")
        
        jwt_headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {encoded_jwt}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        # 2. Get the Installation ID for the specific repository
        try:
            inst_url = f"https://api.github.com/repos/{owner}/{repo}/installation"
            inst_response = httpx.get(inst_url, headers=jwt_headers)
            inst_response.raise_for_status()
            installation_id = inst_response.json()["id"]
            
            # 3. Create an access token for the installation
            token_url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
            token_response = httpx.post(token_url, headers=jwt_headers)
            token_response.raise_for_status()
            installation_token = token_response.json()["token"]
            
            return {
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"Bearer {installation_token}",
                "X-GitHub-Api-Version": "2022-11-28"
            }
        except httpx.HTTPStatusError as e:
            print(f"Error authenticating GitHub App: {e}")
            # Fallback to PAT if App auth fails
            pass

    # Fallback to Personal Access Token
    return {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28"
    }

# Tool to get Pull Request Meta Data
@mcp.tool()
def get_pr_metadata(owner:str,repo:str,pr_number:int):
    url=f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    response=httpx.get(url,headers=get_github_headers(owner, repo))
    response.raise_for_status()
    return response.json()

# Tool to get Pull Request Difference
@mcp.tool()
def get_pr_diff(owner:str,repo:str,pr_number:int):
    url=f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    headers=get_github_headers(owner, repo)
    headers["Accept"]="application/vnd.github.v3.diff"
    response=httpx.get(url,headers=headers)
    return response.text

# Tool to post PR review
@mcp.tool()
def post_pr_review(owner:str,repo:str,pr_number:int,review:str):
    url=f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
    payload={"body":review, "event": "COMMENT"}
    response=httpx.post(url,headers=get_github_headers(owner, repo),json=payload)
    response.raise_for_status()
    return response.json()

# Tool to search codebase
@mcp.tool()
def search_codebase_tool(query: str, n_results: int = 5) -> str:
    """Search the indexed codebase for files related to a natural language query."""
    from agent.search_codebase import search_codebase
    return search_codebase(query, n_results)

# Tool to read a specific file
@mcp.tool()
def read_file_tool(file_path: str, start_line: int = 1, end_line: int = -1) -> str:
    """Read lines from a specific file in the repository. Use start_line and end_line to specify a range."""
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(repo_root, file_path)
    
    # Security check: ensure path is within repo_root
    if not os.path.abspath(full_path).startswith(repo_root):
        return f"Error: Cannot access files outside repository ({file_path})"
        
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        if end_line == -1:
            end_line = len(lines)
            
        # 1-indexed to 0-indexed
        start_idx = max(0, start_line - 1)
        end_idx = min(len(lines), end_line)
        
        output = f"--- {file_path} (lines {start_line}-{end_idx}) ---\n"
        for i, line in enumerate(lines[start_idx:end_idx]):
            output += f"{start_idx + i + 1}: {line}"
            
        return output
    except Exception as e:
        return f"Error reading file: {e}"

if __name__ == "__main__":
    mcp.run()
