from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class Settings(BaseModel):
    app_name: str = "EduGenie"
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "").strip()
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
    explanation_provider: str = os.getenv("EXPLANATION_PROVIDER", "gemini").strip().lower()
    local_explanation_model: str = os.getenv(
        "LOCAL_EXPLANATION_MODEL", "MBZUAI/LaMini-Flan-T5-783M"
    ).strip()
    max_input_chars: int = int(os.getenv("MAX_INPUT_CHARS", "12000"))


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
