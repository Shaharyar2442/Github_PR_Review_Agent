import httpx
from fastmcp import FastMCP
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GITHUB_TOKEN

# Initialize the FastMCP server
mcp = FastMCP("GitHub-Review-Agent")

# Base headers for GitHub API requests
github_headers = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28"
}

# Tool to get Pull Request Meta Data
@mcp.tool()
def get_pr_metadata(owner:str,repo:str,pr_number:int):
    url=f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    response=httpx.get(url,headers=github_headers)
    response.raise_for_status()
    return response.json()


# Tool to get Pull Request Difference
@mcp.tool()
def get_pr_diff(owner:str,repo:str,pr_number:int):
    url=f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    headers=github_headers.copy()
    headers["Accept"]="application/vnd.github.v3.diff"
    response=httpx.get(url,headers=headers)
    return response.text
    


#Tool to post PR review
@mcp.tool()
def post_pr_review(owner:str,repo:str,pr_number:int,review:str):
    url=f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
    payload={"body":review, "event": "COMMENT"}
    response=httpx.post(url,headers=github_headers,json=payload)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":

    mcp.run()
