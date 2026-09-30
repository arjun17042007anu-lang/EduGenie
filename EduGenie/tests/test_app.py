from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


def test_home_loads():
    response = client.get("/")
    assert response.status_code == 200
    assert "EduGenie" in response.text


def test_health_loads():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_qa_with_mock(monkeypatch):
    monkeypatch.setattr(main, "answer_question", lambda text: "Mock answer")
    response = client.post("/qa", json={"text": "What is an ocean?"})
    assert response.status_code == 200
    assert response.json() == {"result": "Mock answer"}


def test_explain_with_mock(monkeypatch):
    monkeypatch.setattr(main, "explain_concept", lambda text: "Simple explanation")
    response = client.post("/explain", json={"text": "Pythagoras theorem"})
    assert response.status_code == 200
    assert response.json()["result"] == "Simple explanation"


def test_quiz_with_mock(monkeypatch):
    fake = [
        {"question": f"Question {i}", "options": ["A", "B", "C", "D"], "correct_answer": "A"}
        for i in range(1, 4)
    ]
    monkeypatch.setattr(main, "generate_quiz", lambda text: fake)
    response = client.post("/quiz", json={"text": "Oceans"})
    assert response.status_code == 200
    assert len(response.json()["result"]) == 3


def test_empty_input_is_rejected():
    response = client.post("/qa", json={"text": "   "})
    assert response.status_code == 422
