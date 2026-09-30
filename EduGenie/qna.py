from __future__ import annotations

from ai_client import generate_text


def answer_question(question: str) -> str:

    prompt = f"""
You are EduGenie, a helpful educational assistant.

Answer the student's question accurately and clearly.
Use simple language.
Give enough explanation to understand the answer.
Include an example when useful.

Student question:
{question}
""".strip()

    return generate_text(prompt)