from __future__ import annotations

from ai_client import generate_text


def summarize_text(text: str) -> str:
    prompt = f"""
You are EduGenie. Summarize the educational passage below for quick revision.
Keep the central facts and relationships, remove repetition, and use clear language.
Return a short paragraph followed by 3-6 key bullet points when appropriate.
Do not add information that is not supported by the passage.

Passage:
{text}
""".strip()
    return generate_text(prompt)
