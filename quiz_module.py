import json
import re
from typing import Any

from gemini_client import generate_text
from prompts import quiz_prompt


def clean_json_block(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _validate_quiz(data: Any) -> dict:
    if not isinstance(data, dict) or not isinstance(data.get("questions"), list):
        raise ValueError("Quiz response does not contain a questions list.")
    if len(data["questions"]) != 3:
        raise ValueError("Quiz must contain exactly 3 questions.")

    for item in data["questions"]:
        if not isinstance(item, dict):
            raise ValueError("Invalid quiz question object.")
        options = item.get("options")
        answer = item.get("answer")
        if not isinstance(options, list) or len(options) != 4:
            raise ValueError("Every question must contain exactly 4 options.")
        if answer not in options:
            raise ValueError("The answer must match one of the options.")
        if not item.get("question"):
            raise ValueError("Question text is missing.")
        item.setdefault("explanation", "")
    return data


def generate_quiz(text: str) -> dict:
    raw = generate_text(quiz_prompt(text))
    try:
        return _validate_quiz(json.loads(clean_json_block(raw)))
    except (json.JSONDecodeError, ValueError) as exc:
        raise RuntimeError(f"Could not parse Gemini quiz JSON: {exc}") from exc
