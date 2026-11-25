"""Reporting utilities for audit logging and GitHub Pull Request comment formatting."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

def save_audit_log(
    log_path: str,
    repo: str,
    pr_number: str,
    model_name: str,
    loaded_rules: list[str],
    result: dict[str, Any],
) -> None:
    """
    Save a structured JSON audit log of the AI review event.

    Args:
        log_path: Destination file path for the JSON log.
        repo: Repository identifier ('owner/repo').
        pr_number: Pull Request number.
        model_name: Identifier of the LLM used for evaluation.
        loaded_rules: List of convention filenames applied during review.
        result: Parsed LLM evaluation result.
    """
    log_entry = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "repository": repo,
        "pr_number": pr_number,
        "model": model_name,
        "applied_conventions": loaded_rules,
        "verdict": result.get("status"),
        "issue_count": len(result.get("issues", [])),
        "details": result,
    }

    target = Path(log_path)
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(log_entry, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        logger.info("Audit log saved to %s.", target)
    except OSError as exc:
        logger.exception("Failed to write audit log to %s: %s", target, exc)
        raise
    
def _format_issues_markdown(issues: list[dict[str, Any]]) -> str:
    """Format a list of convention violation dictionaries into numbered Markdown items."""
    if not issues:
        return "_No detailed issue list provided._"

    blocks = [
        f"{idx}. **`{issue.get('file', 'Unknown file')}`** – *{issue.get('rule', 'Convention violation')}*\n"
        f"   * **Issue:** {issue.get('description', 'Not specified.')}\n"
        f"   * **Suggestion:** {issue.get('suggestion', 'Not specified.')}"
        for idx, issue in enumerate(issues, start=1)
    ]
    return "\n".join(blocks)

def format_pr_comment(
    result: dict[str, Any],
    loaded_rules: list[str],
    human_reviewer: str,
) -> str:
    """Format the LLM verdict into a readable English Markdown comment for GitHub.

    Args:
        result: Parsed LLM evaluation dictionary.
        loaded_rules: List of applied convention filenames.
        human_reviewer: Optional GitHub username to mention for approval or override.

    Returns:
        Formatted Markdown comment string.
    """
    status = str(result.get("status", "FAIL")).upper()
    summary = result.get("summary", "No summary available.")
    issues = result.get("issues", [])
    rules_list = ", ".join(f"`{rule}`" for rule in loaded_rules) or "None"

    if status == "PASS":
        mention = f"@{human_reviewer} " if human_reviewer else ""
        return (
            "## AI Code Convention Review: PASSED\n\n"
            f"**Summary:** {summary}\n\n"
            f"**Applied conventions:** {rules_list}\n\n"
            f"{mention}The changes comply with the coding conventions and are ready "
            "for human review and merging into `main`."
        )

    issues_markdown = _format_issues_markdown(issues)
    override_target = f" (`@{human_reviewer}`)" if human_reviewer else ""
    override_note = (
        f"If this is a false negative, please mention the reviewer{override_target} "
        "in a comment to request a manual override."
    )

    return (
        "## AI Code Convention Review: CHANGES REQUESTED\n\n"
        f"**Summary:** {summary}\n\n"
        f"**Applied conventions:** {rules_list}\n\n"
        f"### Identified Issues\n{issues_markdown}\n\n"
        "---\n"
        f"*{override_note}*"
    )