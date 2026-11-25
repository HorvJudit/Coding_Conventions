"""Configuration module for the AI Pull Request Reviewer.

Loads and validates environment variables and defines static mappings
between source file extensions and coding convention categories.
"""

import os
from dataclasses import dataclass

# Maps lowercase file extensions to the prefix of language-specific convention files
EXTENSION_TO_LANGUAGE: dict[str, str] = {
    ".js": "javascript",
    ".mjs": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".py": "python",
    #".html": "html",
    #".css": "css",
}

DEFAULT_LLM_API_URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
DEFAULT_LLM_MODEL = "gemini-2.5-flash"
DEFAULT_CONVENTIONS_DIR = "coding-conventions/conventions"
DEFAULT_LOG_PATH = "ai_review_log.json"

@dataclass(frozen=True)
class ReviewerConfig:
    """Immutable container for all runtime configuration parameters."""
      
    github_token: str
    repo: str
    pr_number: str
    llm_api_key: str
    llm_api_url: str
    llm_model: str
    conventions_dir: str
    human_reviewer: str
    log_path: str
    
def _get_env(name: str, default: str = "", required: bool = False) -> str:
    """
    Retrieve a trimmed environment variable with optional requirement validation.

    Args:
        name: Name of the environment variable.
        default: Fallback value if the variable is unset or empty.
        required: If True, raises ValueError when the value is missing.

    Returns:
        value: The resolved string value.
    """
    value = os.getenv(name, default).strip()
    if required and not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value

def load_config() -> ReviewerConfig:
    """
    Load and validate all configuration values from the environment.

    Returns:
        A validated, immutable ReviewerConfig instance.
    """
    return ReviewerConfig(
        github_token=_get_env("GITHUB_TOKEN", required=True),
        repo=_get_env("GITHUB_REPOSITORY", required=True),
        pr_number=_get_env("PR_NUMBER", required=True),
        llm_api_key=_get_env("LLM_API_KEY", required=True),
        llm_api_url=_get_env("LLM_API_URL", default=DEFAULT_LLM_API_URL),
        llm_model=_get_env("LLM_MODEL", default=DEFAULT_LLM_MODEL),
        conventions_dir=_get_env("CONVENTIONS_DIR", default=DEFAULT_CONVENTIONS_DIR),
        human_reviewer=_get_env("HUMAN_REVIEWER", default=""),
        log_path=_get_env("LOG_PATH", default=DEFAULT_LOG_PATH),
    )
    
