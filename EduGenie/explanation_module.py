from __future__ import annotations

from functools import lru_cache

from ai_client import AIConfigurationError, AIRequestError, generate_text
from config import get_settings


@lru_cache(maxsize=1)
def _get_local_pipeline():
    settings = get_settings()
    try:
        from transformers import pipeline
    except ImportError as exc:
        raise AIConfigurationError(
            "Local explanation mode requires optional dependencies. "
            "Run: pip install -r requirements-local.txt"
        ) from exc

    try:
        return pipeline(
            "text2text-generation",
            model=settings.local_explanation_model,
            tokenizer=settings.local_explanation_model,
        )
    except Exception as exc:
        raise AIRequestError(f"Could not load local explanation model: {exc}") from exc


def _explain_locally(topic: str) -> str:
    generator = _get_local_pipeline()
    prompt = (
        "Explain the following concept in simple language for a beginner. "
        "Define important terms and give one small example if useful: "
        f"{topic}"
    )
    try:
        output = generator(prompt, max_new_tokens=300, do_sample=False)
        if not output or not output[0].get("generated_text"):
            raise AIRequestError("The local explanation model returned an empty response.")
        return output[0]["generated_text"].strip()
    except AIRequestError:
        raise
    except Exception as exc:
        raise AIRequestError(f"Local explanation generation failed: {exc}") from exc


def explain_concept(topic: str) -> str:
    settings = get_settings()
    if settings.explanation_provider == "local":
        return _explain_locally(topic)

    prompt = f"""
You are EduGenie. Explain the concept below to a beginner.
Use simple, readable language while keeping the explanation technically correct.
Include: a short definition, a step-by-step explanation, and one easy example when useful.
Avoid unnecessary jargon.

Concept:
{topic}
""".strip()
    return generate_text(prompt)
