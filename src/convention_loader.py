"""Loader for core and language-specific Markdown coding convention files."""

import logging
from pathlib import Path
from src.config import EXTENSION_TO_LANGUAGE

logger = logging.getLogger(__name__)

def detect_languages(changed_files: list[str]) -> set[str]:
    """
    Identify programming languages involved in the Pull Request based on file extensions.

    Args:
        changed_files: List of modified file paths.

    Returns:
        Set of matched language identifiers (e.g., {'javascript', 'css'}).
    """
    detected: set[str] = set()
    for filename in changed_files:
        ext = Path(filename).suffix.lower()
        language = EXTENSION_TO_LANGUAGE.get(ext)
        if language:
            detected.add(language)
    return detected

def load_relevant_conventions(
    conventions_dir: str,
    changed_files: list[str],
) -> tuple[str, list[str]]:
    """
    Load core conventions and language-specific conventions matching changed files.

    Args:
        conventions_dir: Path to the directory containing Markdown convention files.
        changed_files: List of modified file paths in the Pull Request.

    Returns:
        A tuple containing:
            - Combined Markdown rules text ready for the LLM prompt.
            - List of loaded convention filenames.
    """
    base_path = Path(conventions_dir)
    if not base_path.exists() or not base_path.is_dir():
        raise FileNotFoundError(f"Conventions directory not found: {conventions_dir}")

    detected_languages = detect_languages(changed_files)
    logger.info("Detected languages in PR: %s", sorted(detected_languages) or "none")

    loaded_files: list[str] = []
    combined_rules: list[str] = []

    for md_file in sorted(base_path.rglob("*.md")):
        name_lower = md_file.name.lower()
        is_core = name_lower.startswith("core")
        is_matching_lang = any(name_lower.startswith(lang) for lang in detected_languages)

        if is_core or is_matching_lang:
            try:
                content = md_file.read_text(encoding="utf-8").strip()
            except OSError as exc:
                logger.warning("Could not read convention file %s: %s", md_file, exc)
                continue

            if content:
                combined_rules.append(f"--- RULE FILE: {md_file.name} ---\n{content}")
                loaded_files.append(md_file.name)

    if not loaded_files:
        logger.warning("No matching convention files were found in %s.", conventions_dir)

    return "\n\n".join(combined_rules), loaded_files