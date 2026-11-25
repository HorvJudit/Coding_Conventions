"""GitHub REST API client for fetching Pull Request data and posting comments."""

import logging
import requests

logger = logging.getLogger(__name__)

GITHUB_API_BASE = "https://api.github.com"
REQUEST_TIMEOUT_SECONDS = 30

def _build_headers(github_token: str, accept: str = "application/vnd.github.v3+json") -> dict[str, str]:
    """Build standardized HTTP headers for GitHub API requests.

    Args:
        github_token: GitHub authentication token.
        accept: Desired Accept media type header.

    Returns:
        Dictionary of HTTP headers.
    """
    return {
        "Authorization": f"Bearer {github_token}",
        "Accept": accept,
    }
    
def fetch_pr_files(repo: str, pr_number: str, github_token: str) -> list[str]:
    """Fetch the list of changed file paths in a Pull Request.

    Args:
        repo: Full repository name in 'owner/repo' format.
        pr_number: Pull Request number as a string.
        github_token: GitHub authentication token.

    Returns:
        List of changed file paths relative to the repository root.
    """
    url = f"{GITHUB_API_BASE}/repos/{repo}/pulls/{pr_number}/files"
    headers = _build_headers(github_token)

    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        files_data = response.json()
        return [item["filename"] for item in files_data if "filename" in item]
    except requests.RequestException as exc:
        logger.exception("Failed to fetch PR files from %s: %s", url, exc)
        raise RuntimeError(f"GitHub API error while fetching PR files: {exc}") from exc
    
def fetch_pr_diff(repo: str, pr_number: str, github_token: str) -> str:
    """Fetch the raw unified diff of a Pull Request.

    Args:
        repo: Full repository name in 'owner/repo' format.
        pr_number: Pull Request number as a string.
        github_token: GitHub authentication token.

    Returns:
        Raw unified diff text.
    """
    url = f"{GITHUB_API_BASE}/repos/{repo}/pulls/{pr_number}"
    headers = _build_headers(github_token, accept="application/vnd.github.v3.diff")

    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        return response.text
    except requests.RequestException as exc:
        logger.exception("Failed to fetch PR diff from %s: %s", url, exc)
        raise RuntimeError(f"GitHub API error while fetching PR diff: {exc}") from exc
    
def post_pr_comment(repo: str, pr_number: str, github_token: str, body: str) -> None:
    """Post a formatted review comment to a GitHub Pull Request.

    Args:
        repo: Full repository name in 'owner/repo' format.
        pr_number: Pull Request number as a string.
        github_token: GitHub authentication token.
        body: Markdown content of the comment.
    """
    url = f"{GITHUB_API_BASE}/repos/{repo}/issues/{pr_number}/comments"
    headers = _build_headers(github_token)

    try:
        response = requests.post(
            url,
            headers=headers,
            json={"body": body},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        logger.info("Successfully posted review comment to PR #%s.", pr_number)
    except requests.RequestException as exc:
        logger.exception("Failed to post PR comment to %s: %s", url, exc)
        raise RuntimeError(f"GitHub API error while posting PR comment: {exc}") from exc