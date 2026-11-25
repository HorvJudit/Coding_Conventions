import json
import logging
from pathlib import Path
from typing import Any
import requests

logger = logging.getLogger(__name__)

LLM_TIMEOUT_SECONDS = 120

def _load_system_prompt(prompt_path: str) -> str:
    """Read the system prompt instructions from an external file.

    Args:
        prompt_path: File system path to the system prompt file.

    Returns:
        Trimmed system prompt content.
    """
    path = Path(prompt_path)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"System prompt file not found: {prompt_path}")

    content = path.read_text(encoding="utf-8").strip()
    if not content:
        raise ValueError(f"System prompt file is empty: {prompt_path}")

    return content

def _extract_json_payload(raw_content: str) -> dict[str, Any]:
    """
    Extract and validate a JSON verdict object from the raw LLM text response.

    Handles responses wrapped in Markdown code fences or surrounding text.

    Args:
        raw_content: Raw string returned by the LLM.

    Returns:
        Parsed dictionary containing the review verdict.
    """
    cleaned = raw_content.strip()

    # Extract the outermost JSON object without regex backtracking
    start_idx = cleaned.find("{")
    end_idx = cleaned.rfind("}")
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        cleaned = cleaned[start_idx : end_idx + 1]

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        logger.error("LLM returned invalid JSON: %s", cleaned)
        raise ValueError(f"Failed to parse LLM response as JSON: {exc}") from exc

    if not isinstance(parsed, dict) or "status" not in parsed:
        raise ValueError("LLM JSON response is missing the required 'status' field.")

    # Normalize expected fields to guarantee downstream consistency
    parsed["status"] = str(parsed["status"]).upper()
    parsed.setdefault("summary", "Nincs elérhető összefoglaló.")
    parsed.setdefault("issues", [])
    return parsed

def evaluate_code(
    diff_text: str,
    rules_text: str,
    system_prompt_path: str,
    api_url: str,
    api_key: str,
    model_name: str,
) -> dict[str, Any]:
    """
    Send the PR diff and coding conventions to the LLM and return the parsed verdict.

    Args:
        diff_text: Unified git diff of the Pull Request.
        rules_text: Combined Markdown coding conventions.
        system_prompt_path: Path to the file containing the system prompt.
        api_url: OpenAI-compatible chat completions endpoint URL.
        api_key: Bearer API key for authentication.
        model_name: Target model identifier.

    Returns:
        Validated dictionary with 'status', 'summary', and 'issues'.
    """
    system_prompt = _load_system_prompt(system_prompt_path)
    user_prompt = (
        f"### CODING CONVENTIONS ###\n{rules_text}\n\n"
        f"### PULL REQUEST DIFF ###\n{diff_text}"
    )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model_name,
        "temperature": 0.1,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    try:
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=LLM_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        response_data = response.json()
        raw_content = response_data["choices"][0]["message"]["content"]
    except requests.RequestException as exc:
        logger.exception("LLM API request failed: %s", exc)
        raise RuntimeError(f"LLM API communication error: {exc}") from exc
    except (KeyError, IndexError, TypeError) as exc:
        logger.exception("Unexpected LLM API response structure: %s", exc)
        raise RuntimeError(f"Malformed LLM API response structure: {exc}") from exc

    return _extract_json_payload(raw_content)