from __future__ import annotations

import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


class AIConfigurationError(RuntimeError):
    pass


class AIRequestError(RuntimeError):
    pass


_client = None


def get_client() -> genai.Client:
    global _client

    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise AIConfigurationError(
                "GEMINI_API_KEY is missing from .env"
            )

        _client = genai.Client(api_key=api_key)

    return _client


def get_model_name() -> str:
    return os.getenv("GEMINI_MODEL", "gemini-3.8-flash")


def generate_text(prompt: str) -> str:

    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    model = get_model_name()

    try:
        response = get_client().models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
            ),
        )

        answer = getattr(response, "text", None)

        if not answer:
            raise AIRequestError(
                f"Gemini returned an empty response using {model}."
            )

        return answer.strip()

    except AIConfigurationError:
        raise

    except Exception as exc:
        error = str(exc)

        if "429" in error or "RESOURCE_EXHAUSTED" in error:
            raise AIRequestError(
                "Gemini API quota/rate limit exceeded. "
                "Please wait for the quota to reset or check "
                "your Google AI Studio quota."
            ) from exc

        raise AIRequestError(
            f"Gemini request failed using model '{model}': {exc}"
        ) from exc