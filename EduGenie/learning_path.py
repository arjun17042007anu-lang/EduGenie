from __future__ import annotations

from ai_client import generate_text


def get_learning_recommendations(topic: str) -> str:
    prompt = f"""
You are EduGenie, an educational planning assistant.
Create a practical learning path for: {topic}

Structure it from beginner to advanced. Include:
1. Prerequisites
2. Beginner concepts
3. Intermediate concepts
4. Advanced concepts
5. A realistic study sequence with suggested time ranges
6. Practice/project ideas
7. Resource TYPES to look for (official docs, textbooks, lectures, exercises)

Do not fabricate URLs. Keep the plan adaptable for a self-learner.
""".strip()
    return generate_text(prompt)
