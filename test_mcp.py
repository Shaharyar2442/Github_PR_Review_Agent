import sys
from github_mcp.server import get_pr_metadata, get_pr_diff, post_pr_review

# ─── YOUR TURN ──────────────────────────────────────────────
# Goal: Test your MCP tools on a real Pull Request.
# Hint: First, go to your GitHub repository (Shaharyar2442/Github_PR_Review_Agent)
#       and create a quick dummy Pull Request (you can just create a new branch, 
#       add a blank file, and open a PR). Then, enter the PR number below.
# Expected result: The script will print the PR metadata, the diff, and post a test comment.
# ────────────────────────────────────────────────────────────

OWNER = "Shaharyar2442"
REPO = "Github_PR_Review_Agent"
PR_NUMBER = 1  # <-- Change this to your actual test PR number!

def main():
    print(f"--- Fetching Metadata for PR #{PR_NUMBER} ---")
    try:
        metadata = get_pr_metadata(OWNER, REPO, PR_NUMBER)
        print(f"Title: {metadata.get('title')}")
        print(f"State: {metadata.get('state')}")
    except Exception as e:
        print(f"Failed to fetch metadata: {e}")
        return
    print("\n")

    print(f"--- Fetching Diff for PR #{PR_NUMBER} ---")
    try:
        diff = get_pr_diff(OWNER, REPO, PR_NUMBER)
        print("Diff Snippet (first 200 chars):")
        print(diff[:200])
    except Exception as e:
        print(f"Failed to fetch diff: {e}")
    print("\n")

    print(f"--- Posting Test Review to PR #{PR_NUMBER} ---")
    # Be careful, this will actually post a comment on your PR!
    review_text = "Hello from my custom MCP server! :robot:"
    try:
        review_result = post_pr_review(OWNER, REPO, PR_NUMBER, review_text)
        print(f"Review posted! URL: {review_result.get('html_url')}")
    except Exception as e:
        print(f"Failed to post review: {e}")

if __name__ == "__main__":
    main()
