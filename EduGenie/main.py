from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, field_validator

from ai_client import AIConfigurationError, AIRequestError
from config import get_settings
from explanation_module import explain_concept
from learning_path import get_learning_recommendations
from qna import answer_question
from quiz_module import generate_quiz
from summary_module import summarize_text

BASE_DIR = Path(__file__).resolve().parent
settings = get_settings()

app = FastAPI(
    title="EduGenie API",
    description="Google Gemini powered learning assistant",
    version="1.0.0",
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


class TextRequest(BaseModel):
    text: str = Field(..., min_length=1)

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Input cannot be empty.")
        max_chars = get_settings().max_input_chars
        if len(value) > max_chars:
            raise ValueError(f"Input is too long. Maximum allowed length is {max_chars} characters.")
        return value


class TextResponse(BaseModel):
    result: str


class QuizItem(BaseModel):
    question: str
    options: list[str]
    correct_answer: str


class QuizResponse(BaseModel):
    result: list[QuizItem]


def _raise_http_error(exc: Exception) -> None:
    if isinstance(exc, AIConfigurationError):
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    if isinstance(exc, AIRequestError):
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    raise HTTPException(status_code=500, detail=f"Unexpected server error: {exc}") from exc


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"app_name": settings.app_name},
    )


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "app": settings.app_name,
        "gemini_configured": bool(settings.gemini_api_key),
        "gemini_model": settings.gemini_model,
        "explanation_provider": settings.explanation_provider,
    }


@app.post("/qa", response_model=TextResponse)
def qa(payload: TextRequest) -> TextResponse:
    try:
        return TextResponse(result=answer_question(payload.text))
    except Exception as exc:
        _raise_http_error(exc)


@app.post("/explain", response_model=TextResponse)
def explain(payload: TextRequest) -> TextResponse:
    try:
        return TextResponse(result=explain_concept(payload.text))
    except Exception as exc:
        _raise_http_error(exc)


@app.post("/quiz", response_model=QuizResponse)
def quiz(payload: TextRequest) -> QuizResponse:
    try:
        return QuizResponse(result=generate_quiz(payload.text))
    except Exception as exc:
        _raise_http_error(exc)


@app.post("/summarize", response_model=TextResponse)
def summarize(payload: TextRequest) -> TextResponse:
    try:
        return TextResponse(result=summarize_text(payload.text))
    except Exception as exc:
        _raise_http_error(exc)


@app.post("/learn/recommendations", response_model=TextResponse)
def recommendations(payload: TextRequest) -> TextResponse:
    try:
        return TextResponse(result=get_learning_recommendations(payload.text))
    except Exception as exc:
        _raise_http_error(exc)
