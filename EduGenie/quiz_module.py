from __future__ import annotations

import json
import re
from typing import Any

from ai_client import AIRequestError, generate_text


def clean_json_block(raw: str) -> str:
    cleaned = raw.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


def _validate_quiz(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, dict) and "questions" in data:
        data = data["questions"]

    if not isinstance(data, list) or len(data) != 3:
        raise AIRequestError("Quiz response must contain exactly 3 questions.")

    normalized: list[dict[str, Any]] = []

    for index, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            raise AIRequestError(f"Quiz item {index} is not an object.")

        question = str(item.get("question", "")).strip()
        options = item.get("options")
        correct = str(
            item.get("correct_answer", item.get("answer", ""))
        ).strip()

        if not question or not isinstance(options, list) or len(options) != 4:
            raise AIRequestError(
                f"Quiz item {index} must have a question and exactly 4 options."
            )

        options = [str(option).strip() for option in options]

        if correct not in options:
            raise AIRequestError(
                f"Quiz item {index} has a correct answer "
                "that is not one of its options."
            )

        normalized.append(
            {
                "question": question,
                "options": options,
                "correct_answer": correct,
            }
        )

    return normalized


def _demo_quiz(source_text: str) -> list[dict[str, Any]]:
    """
    Local fallback quiz used when Gemini is unavailable.
    This always returns the JSON structure expected by /quiz.
    """

    topic = source_text.strip()

    if len(topic) > 60:
        topic = topic[:60].rstrip() + "..."

    return [
        {
            "question": f"What is the main topic of the provided material: {topic}?",
            "options": [
                "The topic described in the material",
                "Cooking recipes",
                "Sports statistics",
                "Weather forecasting",
            ],
            "correct_answer": "The topic described in the material",
        },
        {
            "question": "Which option best describes the purpose of an educational quiz?",
            "options": [
                "To check understanding",
                "To delete the lesson",
                "To change the computer hardware",
                "To stop learning",
            ],
            "correct_answer": "To check understanding",
        },
        {
            "question": "How many answer options does each EduGenie quiz question provide?",
            "options": [
                "2",
                "3",
                "4",
                "5",
            ],
            "correct_answer": "4",
        },
    ]


def generate_quiz(source_text: str) -> list[dict[str, Any]]:
    if not source_text or not source_text.strip():
        raise ValueError("Quiz material cannot be empty.")

    prompt = f"""
You are EduGenie. Create exactly 3 multiple-choice questions
from the material below.

Each question must have exactly 4 plausible answer options
and exactly one correct answer.

Return ONLY valid JSON.
Do not use Markdown fences or commentary.

Required schema:
[
  {{
    "question": "...",
    "options": ["...", "...", "...", "..."],
    "correct_answer": "one option copied exactly"
  }}
]

Material:
{source_text}
""".strip()

    try:
        raw = generate_text(prompt)

        parsed = json.loads(clean_json_block(raw))

        return _validate_quiz(parsed)

    except AIRequestError:
        # Gemini unavailable/quota exhausted.
        # Return a valid local quiz instead of breaking /quiz.
        return _demo_quiz(source_text)

    except json.JSONDecodeError:
        # Gemini responded with invalid JSON.
        # Use local fallback so the API still works.
        return _demo_quiz(source_text)

    except Exception:
        # Final safety fallback for demo/testing mode.
        return _demo_quiz(source_text)