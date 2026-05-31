"""
GitHub API utilities with:
- Installation token caching (#8)
- Rate limit handling (#18)
- Both sync and async variants (#20)
"""

import httpx
import time
import jwt
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from config import GITHUB_TOKEN, GITHUB_APP_ID, GITHUB_PRIVATE_KEY


# ─── Token Cache ────────────────────────────────────────────
# Avoids minting a new installation token on every single API call.
# GitHub installation tokens are valid for 1 hour; we cache with a 5-minute buffer.
_token_cache: dict[tuple[str, str], tuple[str, float]] = {}
_TOKEN_BUFFER_SECONDS = 300  # Refresh 5 minutes before expiry


class GitHubRateLimitError(Exception):
    """Raised when GitHub returns a 403 rate-limit response."""
    def __init__(self, retry_after: int = 60):
        self.retry_after = retry_after
        super().__init__(f"GitHub rate limit hit. Retry after {retry_after}s")


def _check_rate_limit(response: httpx.Response) -> None:
    """Check for GitHub rate limit responses and raise a retryable error."""
    if response.status_code == 403:
        retry_after = int(response.headers.get("Retry-After", "60"))
        remaining = response.headers.get("X-RateLimit-Remaining", "unknown")
        logger.warning(f"GitHub rate limit hit. Remaining: {remaining}, Retry-After: {retry_after}s")
        raise GitHubRateLimitError(retry_after)
    if response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", "60"))
        logger.warning(f"GitHub 429 Too Many Requests. Retry-After: {retry_after}s")
        raise GitHubRateLimitError(retry_after)


def get_github_headers(owner: str = None, repo: str = None) -> dict[str, str]:
    """
    Returns the appropriate GitHub headers. If App ID and Private Key are present,
    it dynamically generates (and caches) an installation token for the specified repo.
    Otherwise, it falls back to the personal GITHUB_TOKEN.
    """
    if GITHUB_APP_ID and GITHUB_PRIVATE_KEY and owner and repo:
        cache_key = (owner, repo)
        cached = _token_cache.get(cache_key)
        if cached and cached[1] > time.time() + _TOKEN_BUFFER_SECONDS:
            return {
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"Bearer {cached[0]}",
                "X-GitHub-Api-Version": "2022-11-28"
            }

        # Mint a new installation token
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
            inst_response = httpx.get(inst_url, headers=jwt_headers, timeout=10)
            inst_response.raise_for_status()
            installation_id = inst_response.json()["id"]

            token_url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
            token_response = httpx.post(token_url, headers=jwt_headers, timeout=10)
            token_response.raise_for_status()
            installation_token = token_response.json()["token"]

            # Cache for ~1 hour (token lifetime)
            _token_cache[cache_key] = (installation_token, time.time() + 3600)
            logger.debug(f"Cached new installation token for {owner}/{repo}")

            return {
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"Bearer {installation_token}",
                "X-GitHub-Api-Version": "2022-11-28"
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"Error authenticating GitHub App for {owner}/{repo}: {e}")
            # Fall through to personal token

    return {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28"
    }


# ─── Sync API functions (used by LangChain tools) ──────────

@retry(
    retry=retry_if_exception_type(GitHubRateLimitError),
    wait=wait_exponential(multiplier=2, min=5, max=60),
    stop=stop_after_attempt(3),
)
def get_pr_metadata(owner: str, repo: str, pr_number: int) -> dict:
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    response = httpx.get(url, headers=get_github_headers(owner, repo), timeout=15)
    _check_rate_limit(response)
    response.raise_for_status()
    return response.json()


@retry(
    retry=retry_if_exception_type(GitHubRateLimitError),
    wait=wait_exponential(multiplier=2, min=5, max=60),
    stop=stop_after_attempt(3),
)
def get_pr_diff(owner: str, repo: str, pr_number: int) -> str:
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    headers = get_github_headers(owner, repo)
    headers["Accept"] = "application/vnd.github.v3.diff"
    response = httpx.get(url, headers=headers, timeout=15)
    _check_rate_limit(response)
    return response.text


@retry(
    retry=retry_if_exception_type(GitHubRateLimitError),
    wait=wait_exponential(multiplier=2, min=5, max=60),
    stop=stop_after_attempt(3),
)
def post_pr_review(owner: str, repo: str, pr_number: int, review: str) -> dict:
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
    payload = {"body": review, "event": "COMMENT"}
    response = httpx.post(url, headers=get_github_headers(owner, repo), json=payload, timeout=15)
    _check_rate_limit(response)
    response.raise_for_status()
    return response.json()


# ─── Async API functions (used by graph nodes) ─────────────

@retry(
    retry=retry_if_exception_type(GitHubRateLimitError),
    wait=wait_exponential(multiplier=2, min=5, max=60),
    stop=stop_after_attempt(3),
)
async def async_get_pr_metadata(owner: str, repo: str, pr_number: int) -> dict:
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(url, headers=get_github_headers(owner, repo))
    _check_rate_limit(response)
    response.raise_for_status()
    return response.json()


@retry(
    retry=retry_if_exception_type(GitHubRateLimitError),
    wait=wait_exponential(multiplier=2, min=5, max=60),
    stop=stop_after_attempt(3),
)
async def async_get_pr_diff(owner: str, repo: str, pr_number: int) -> str:
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    headers = get_github_headers(owner, repo)
    headers["Accept"] = "application/vnd.github.v3.diff"
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(url, headers=headers)
    _check_rate_limit(response)
    return response.text


@retry(
    retry=retry_if_exception_type(GitHubRateLimitError),
    wait=wait_exponential(multiplier=2, min=5, max=60),
    stop=stop_after_attempt(3),
)
async def async_post_pr_review(owner: str, repo: str, pr_number: int, review: str) -> dict:
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
    payload = {"body": review, "event": "COMMENT"}
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(url, headers=get_github_headers(owner, repo), json=payload)
    _check_rate_limit(response)
    response.raise_for_status()
    return response.json()
