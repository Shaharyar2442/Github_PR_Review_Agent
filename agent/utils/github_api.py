import httpx
import time
import jwt
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import GITHUB_TOKEN, GITHUB_APP_ID, GITHUB_PRIVATE_KEY

def get_github_headers(owner: str = None, repo: str = None):
    """
    Returns the appropriate GitHub headers. If App ID and Private Key are present,
    it dynamically generates an installation token for the specified repo.
    Otherwise, it falls back to the personal GITHUB_TOKEN.
    """
    if GITHUB_APP_ID and GITHUB_PRIVATE_KEY and owner and repo:
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
        
        try:
            inst_url = f"https://api.github.com/repos/{owner}/{repo}/installation"
            inst_response = httpx.get(inst_url, headers=jwt_headers)
            inst_response.raise_for_status()
            installation_id = inst_response.json()["id"]
            
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
            pass

    return {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28"
    }

def get_pr_metadata(owner: str, repo: str, pr_number: int):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    response = httpx.get(url, headers=get_github_headers(owner, repo))
    response.raise_for_status()
    return response.json()

def get_pr_diff(owner: str, repo: str, pr_number: int):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    headers = get_github_headers(owner, repo)
    headers["Accept"] = "application/vnd.github.v3.diff"
    response = httpx.get(url, headers=headers)
    return response.text

def post_pr_review(owner: str, repo: str, pr_number: int, review: str):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
    payload = {"body": review, "event": "COMMENT"}
    response = httpx.post(url, headers=get_github_headers(owner, repo), json=payload)
    response.raise_for_status()
    return response.json()
