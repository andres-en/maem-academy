"""Enrollment, progress tracking, graded assessments and due dates."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from tests.helpers import add_module_with_lesson, add_quiz, create_course, enroll, publish


@pytest.fixture
def published_course(client, make_user):
    """A published course with 2 lessons and a required quiz (pass mark 60%, 2 attempts)."""
    _, instructor = make_user("INSTRUCTOR")
    _, admin = make_user("ADMIN")
    course = create_course(client, instructor)
    _, lesson_ids = add_module_with_lesson(client, instructor, course["id"], lessons=2)
    quiz = add_quiz(client, instructor, course["id"])
    publish(client, course_id=course["id"], author=instructor, reviewer=admin)
    return {"id": course["id"], "lessons": lesson_ids, "quiz": quiz, "admin": admin}


@pytest.fixture
def learner(client, make_user, published_course):
    user_id, headers = make_user("USER")
    result = enroll(client, published_course["admin"], published_course["id"], [user_id])
    return {"id": user_id, "headers": headers, "enrollment_id": result["enrollments"][0]["id"]}


def _content(client, learner):
    return client.get(f"/api/v1/enrollments/{learner['enrollment_id']}/content", headers=learner["headers"]).json()


def _complete_all_lessons(client, learner, course):
    for lesson_id in course["lessons"]:
        resp = client.post(
            f"/api/v1/enrollments/{learner['enrollment_id']}/lessons/{lesson_id}/complete", headers=learner["headers"]
        )
        assert resp.status_code == 200, resp.text


def _attempt(client, learner, quiz, option_id):
    base = f"/api/v1/enrollments/{learner['enrollment_id']}"
    started = client.post(f"{base}/assessments/{quiz['id']}/start", headers=learner["headers"])
    assert started.status_code == 200, started.text
    body = {"answers": [{"question_id": quiz["question_id"], "selected_option_id": option_id}]}
    return client.post(f"{base}/attempts/{started.json()['attempt_id']}/submit", json=body, headers=learner["headers"])


def test_only_published_courses_accept_enrollments(client, make_user):
    _, instructor = make_user("INSTRUCTOR")
    _, admin = make_user("ADMIN")
    user_id, _ = make_user("USER")
    draft = create_course(client, instructor)
    resp = client.post(f"/api/v1/courses/{draft['id']}/enrollments", json={"user_ids": [str(user_id)]}, headers=admin)
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Users can only be enrolled in published courses."


def test_enrolling_twice_is_idempotent(client, published_course, learner):
    again = enroll(client, published_course["admin"], published_course["id"], [learner["id"]])
    assert again["created"] == 0
    assert again["skipped"] == 1


def test_group_assignment_creates_one_enrollment_per_member(client, make_user, published_course):
    admin = published_course["admin"]
    members = [make_user("USER")[0] for _ in range(3)]
    group = client.post(
        "/api/v1/groups", json={"name": "New hires", "user_ids": [str(m) for m in members]}, headers=admin
    )
    assert group.status_code == 201, group.text

    resp = client.post(
        f"/api/v1/courses/{published_course['id']}/assignments",
        json={"group_ids": [group.json()["id"]], "is_required": True},
        headers=admin,
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["enrollments_created"] == 3


def test_learners_only_see_their_own_enrollments(client, make_user, learner):
    _, other = make_user("USER")
    resp = client.get(f"/api/v1/enrollments/{learner['enrollment_id']}/content", headers=other)
    assert resp.status_code == 403
    assert resp.json()["detail"] == "This enrollment does not belong to you."


def test_opening_the_course_starts_it_and_lessons_drive_progress(client, published_course, learner):
    assert _content(client, learner)["enrollment"]["status"] == "IN_PROGRESS"

    base = f"/api/v1/enrollments/{learner['enrollment_id']}/lessons"
    first = client.post(f"{base}/{published_course['lessons'][0]}/complete", headers=learner["headers"]).json()
    assert first["enrollment"]["progress_percentage"] == 50.0

    second = client.post(f"{base}/{published_course['lessons'][1]}/complete", headers=learner["headers"]).json()
    assert second["enrollment"]["progress_percentage"] == 100.0
    # The required quiz is still pending, so the course is not finished yet.
    assert second["enrollment"]["status"] == "IN_PROGRESS"


def test_lessons_from_another_course_are_rejected(client, make_user, learner):
    _, instructor = make_user("INSTRUCTOR")
    other = create_course(client, instructor)
    _, (foreign_lesson,) = add_module_with_lesson(client, instructor, other["id"])
    resp = client.post(
        f"/api/v1/enrollments/{learner['enrollment_id']}/lessons/{foreign_lesson}/complete", headers=learner["headers"]
    )
    assert resp.status_code == 400


def test_started_attempts_never_reveal_the_correct_answer(client, published_course, learner):
    started = client.post(
        f"/api/v1/enrollments/{learner['enrollment_id']}/assessments/{published_course['quiz']['id']}/start",
        headers=learner["headers"],
    ).json()
    options = started["questions"][0]["options"]
    assert all(set(option) == {"id", "text"} for option in options)


def test_passing_the_quiz_after_all_lessons_marks_the_course_as_passed(client, published_course, learner):
    _complete_all_lessons(client, learner, published_course)
    result = _attempt(client, learner, published_course["quiz"], published_course["quiz"]["correct"]).json()
    assert result["score"] == 100.0
    assert result["status"] == "PASSED"
    assert _content(client, learner)["enrollment"]["status"] == "PASSED"


def test_failing_every_allowed_attempt_fails_the_enrollment(client, published_course, learner):
    quiz = published_course["quiz"]
    first = _attempt(client, learner, quiz, quiz["wrong"]).json()
    assert (first["score"], first["status"]) == (0.0, "FAILED")
    assert _content(client, learner)["enrollment"]["status"] == "IN_PROGRESS"  # one attempt left

    _attempt(client, learner, quiz, quiz["wrong"])
    assert _content(client, learner)["enrollment"]["status"] == "FAILED"

    third = client.post(
        f"/api/v1/enrollments/{learner['enrollment_id']}/assessments/{quiz['id']}/start", headers=learner["headers"]
    )
    assert third.status_code in (400, 403)


def test_an_attempt_cannot_be_submitted_twice(client, published_course, learner):
    quiz = published_course["quiz"]
    base = f"/api/v1/enrollments/{learner['enrollment_id']}"
    attempt_id = client.post(f"{base}/assessments/{quiz['id']}/start", headers=learner["headers"]).json()["attempt_id"]
    body = {"answers": [{"question_id": quiz["question_id"], "selected_option_id": quiz["correct"]}]}
    assert client.post(f"{base}/attempts/{attempt_id}/submit", json=body, headers=learner["headers"]).status_code == 200
    again = client.post(f"{base}/attempts/{attempt_id}/submit", json=body, headers=learner["headers"])
    assert again.status_code == 400
    assert again.json()["detail"] == "This attempt was already submitted."


def test_questions_need_exactly_one_correct_option(client, make_user):
    _, instructor = make_user("INSTRUCTOR")
    course = create_course(client, instructor)
    assessment = client.post(
        f"/api/v1/courses/{course['id']}/assessments", json={"title": "Quiz"}, headers=instructor
    ).json()
    two_correct = [{"text": "a", "is_correct": True}, {"text": "b", "is_correct": True}]
    resp = client.post(
        f"/api/v1/assessments/{assessment['id']}/questions",
        json={"question_text": "?", "options": two_correct},
        headers=instructor,
    )
    assert resp.status_code in (400, 422)


def test_overdue_blocking_assignment_locks_the_course(client, make_user, published_course):
    admin = published_course["admin"]
    user_id, headers = make_user("USER")
    assignment = client.post(
        f"/api/v1/courses/{published_course['id']}/assignments",
        json={"user_ids": [str(user_id)], "is_required": True, "overdue_action": "BLOCK"},
        headers=admin,
    )
    assert assignment.status_code == 201, assignment.text
    enrollment_id = client.get("/api/v1/enrollments/me", headers=headers).json()[0]["id"]

    past = (datetime.now(UTC) - timedelta(days=1)).isoformat()
    updated = client.patch(f"/api/v1/enrollments/{enrollment_id}", json={"due_date": past}, headers=admin)
    assert updated.status_code == 200, updated.text

    resp = client.get(f"/api/v1/enrollments/{enrollment_id}/content", headers=headers)
    assert resp.status_code == 403
    assert resp.json()["detail"] == "This enrollment is past its due date and the course is blocked."


def test_cancelled_enrollments_lose_access(client, published_course, learner):
    admin = published_course["admin"]
    assert client.post(f"/api/v1/enrollments/{learner['enrollment_id']}/cancel", headers=admin).status_code == 200
    resp = client.get(f"/api/v1/enrollments/{learner['enrollment_id']}/content", headers=learner["headers"])
    assert resp.status_code == 403
    again = client.post(f"/api/v1/enrollments/{learner['enrollment_id']}/cancel", headers=admin)
    assert again.status_code == 400


def test_reports_reflect_learner_outcomes(client, published_course, learner):
    quiz = published_course["quiz"]
    _complete_all_lessons(client, learner, published_course)
    _attempt(client, learner, quiz, quiz["correct"])

    admin = published_course["admin"]
    summary = client.get("/api/v1/reports/summary", headers=admin).json()
    assert summary["published_courses"] == 1
    assert summary["passed"] == 1

    rows = client.get(f"/api/v1/reports/courses/{published_course['id']}", headers=admin).json()
    assert rows[0]["status"] == "PASSED"
    assert rows[0]["score"] == 100.0
