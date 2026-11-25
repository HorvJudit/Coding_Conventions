"""Entry point for the automated AI Pull Request convention reviewer."""

import logging
import sys
from src.config import load_config
from src.convention_loader import load_relevant_conventions
from src.github_client import fetch_pr_diff, fetch_pr_files, post_pr_comment
from src.llm_client import evaluate_code
from src.reporting import format_pr_comment, save_audit_log

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

def run_review() -> None:
    """Execute the end-to-end Pull Request convention review workflow."""
    config = load_config()
    logger.info("Starting AI review for %s PR #%s.", config.repo, config.pr_number)

    changed_files = fetch_pr_files(config.repo, config.pr_number, config.github_token)
    diff_text = fetch_pr_diff(config.repo, config.pr_number, config.github_token)
    
    if not diff_text.strip():
        logger.info("Pull Request #%s has an empty diff. Skipping review.", config.pr_number)
        return
    
    rules_text, loaded_rules = load_relevant_conventions(
        config.conventions_dir,
        changed_files,
    )
    if not rules_text.strip():
        logger.warning("No applicable coding conventions loaded. Skipping LLM evaluation.")
        return
    
    result = evaluate_code(
        diff_text=diff_text,
        rules_text=rules_text,
        system_prompt_path=config.system_prompt_path,
        api_url=config.llm_api_url,
        api_key=config.llm_api_key,
        model_name=config.llm_model,
    )
    
    save_audit_log(
        log_path=config.log_path,
        repo=config.repo,
        pr_number=config.pr_number,
        model_name=config.llm_model,
        loaded_rules=loaded_rules,
        result=result,
    )
    
    comment_body = format_pr_comment(result, loaded_rules, config.human_reviewer)
    post_pr_comment(config.repo, config.pr_number, config.github_token, comment_body)

    logger.info(
        "Review completed for PR #%s. Verdict: %s.",
        config.pr_number,
        result.get("status"),
    )


def main() -> None:
    """CLI entry point with top-level error handling for CI/CD pipelines."""
    try:
        run_review()
    except Exception as exc:
        logger.exception("AI Pull Request review failed: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()