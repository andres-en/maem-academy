"""Small builders shared by the API tests."""

from __future__ import annotations


def create_course(client, headers, title: str = "Security Awareness", **extra) -> dict:
    resp = client.post("/api/v1/courses", json={"title": title, **extra}, headers=headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


def add_module_with_lesson(client, headers, course_id: str, *, lessons: int = 1) -> tuple[str, list[str]]:
    module = client.post(f"/api/v1/courses/{course_id}/modules", json={"title": "Module 1"}, headers=headers).json()
    lesson_ids = []
    for i in range(lessons):
        lesson = client.post(
            f"/api/v1/course-modules/{module['id']}/lessons", json={"title": f"Lesson {i + 1}"}, headers=headers
        ).json()
        client.post(
            f"/api/v1/lessons/{lesson['id']}/contents",
            data={"content_type": "TEXT", "text_content": "Read this."},
            headers=headers,
        )
        lesson_ids.append(lesson["id"])
    return module["id"], lesson_ids


def add_quiz(client, headers, course_id: str, *, minimum_score: float = 60, max_attempts: int | None = 2) -> dict:
    """A one-question assessment; returns the assessment with its question and option ids."""
    assessment = client.post(
        f"/api/v1/courses/{course_id}/assessments",
        json={"title": "Final quiz", "minimum_score": minimum_score, "max_attempts": max_attempts, "is_required": True},
        headers=headers,
    ).json()
    question = client.post(
        f"/api/v1/assessments/{assessment['id']}/questions",
        json={
            "question_text": "What should you do with a suspicious email?",
            "points": 1,
            "options": [
                {"text": "Report it", "is_correct": True},
                {"text": "Open the attachment", "is_correct": False},
            ],
        },
        headers=headers,
    ).json()
    correct = next(o["id"] for o in question["options"] if o["is_correct"])
    wrong = next(o["id"] for o in question["options"] if not o["is_correct"])
    return {"id": assessment["id"], "question_id": question["id"], "correct": correct, "wrong": wrong}


def publish(client, *, course_id: str, author, reviewer) -> None:
    assert client.post(f"/api/v1/courses/{course_id}/submit-review", headers=author).status_code == 200
    assert client.post(f"/api/v1/courses/{course_id}/approve", headers=reviewer).status_code == 200
    assert client.post(f"/api/v1/courses/{course_id}/publish", headers=reviewer).status_code == 200


def enroll(client, headers, course_id: str, user_ids: list, **extra) -> dict:
    resp = client.post(
        f"/api/v1/courses/{course_id}/enrollments",
        json={"user_ids": [str(u) for u in user_ids], **extra},
        headers=headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()
