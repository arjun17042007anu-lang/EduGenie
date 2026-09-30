# EduGenie — Google Gemini Powered Learning Assistant

EduGenie is a FastAPI + HTML/CSS/JavaScript educational assistant with five features:

- Question answering
- Beginner-friendly concept explanation
- 3-question MCQ quiz generation
- Educational text summarization
- Beginner-to-advanced learning-path recommendations

## Project structure

```text
EduGenie/
├── main.py
├── config.py
├── ai_client.py
├── qna.py
├── explanation_module.py
├── quiz_module.py
├── summary_module.py
├── learning_path.py
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── app.js
├── tests/
│   └── test_app.py
├── .env.example
├── .gitignore
├── requirements.txt
└── requirements-local.txt
```

## 1. Prerequisites

- Python 3.10 or newer
- VS Code
- A Google AI Studio Gemini API key

## 2. Open in VS Code

Open VS Code, choose **File → Open Folder**, and open the `EduGenie` folder.

Open the integrated terminal with **Terminal → New Terminal**.

## 3. Create and activate a virtual environment

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run this once in that terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate again.

### Windows Command Prompt

```bat
py -m venv .venv
.venv\Scripts\activate.bat
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

In VS Code, press `Ctrl+Shift+P` / `Cmd+Shift+P`, choose **Python: Select Interpreter**, and select `.venv`.

## 4. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Configure Gemini

Copy `.env.example` to `.env`.

### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

### Windows Command Prompt

```bat
copy .env.example .env
```

### macOS / Linux

```bash
cp .env.example .env
```

Edit `.env` and set:

```env
GEMINI_API_KEY=your_real_api_key_here
GEMINI_MODEL=gemini-2.5-flash
EXPLANATION_PROVIDER=gemini
```

`GEMINI_MODEL` is configurable because model availability can differ by Google AI Studio account and over time. If that model is not enabled, replace it with a Gemini model available to your account.

## 6. Run EduGenie

```bash
uvicorn main:app --reload
```

Open:

- Application: http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

Stop the server with `Ctrl+C`.

## 7. Test the application

The included unit/API tests mock AI calls, so they do **not** spend Gemini API quota:

```bash
pytest -q
```

You can also manually test the live Gemini API from Swagger at http://127.0.0.1:8000/docs.

Example POST body for `/qa`:

```json
{
  "text": "Which is the largest ocean?"
}
```

## 8. Optional: use the documented local LaMini model for explanations

The project documentation assigns concept explanation to `MBZUAI/LaMini-Flan-T5-783M`. The default setup uses Gemini for explanations because it is much lighter to install.

To enable the local model:

```bash
pip install -r requirements-local.txt
```

Then edit `.env`:

```env
EXPLANATION_PROVIDER=local
LOCAL_EXPLANATION_MODEL=MBZUAI/LaMini-Flan-T5-783M
```

The model is downloaded on first use and requires substantially more disk space/RAM than the normal Gemini setup.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Web UI |
| GET | `/health` | Configuration/health status |
| POST | `/qa` | Question answering |
| POST | `/explain` | Concept explanation |
| POST | `/quiz` | Generate 3 MCQs |
| POST | `/summarize` | Summarize educational text |
| POST | `/learn/recommendations` | Generate a learning path |

All POST endpoints accept JSON in this form:

```json
{ "text": "your input here" }
```

## Common errors

### `503 GEMINI_API_KEY is missing`
Create `.env` from `.env.example`, put the real API key in it, then restart Uvicorn.

### `502 Gemini request failed ... model ...`
The API key may be invalid, the model may not be available to the account, or Google may be returning an upstream error. Change `GEMINI_MODEL` to a model enabled in your Google AI Studio project and restart the server.

### Browser shows `500 Internal Server Error`
Read the Uvicorn terminal first. This build converts expected AI/provider failures into descriptive HTTP 502/503 responses, so a true HTTP 500 generally points to an unexpected Python/runtime error.

### Local model is slow or fails to install
Switch `.env` back to `EXPLANATION_PROVIDER=gemini`. The local LaMini model is optional and much heavier than the cloud setup.
