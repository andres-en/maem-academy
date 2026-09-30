"""Editorial workflow: DRAFT -> IN_REVIEW -> (CHANGES_REQUESTED | APPROVED) -> PUBLISHED -> ARCHIVED."""

from __future__ import annotations

from tests.helpers import add_module_with_lesson, create_course, publish


def test_happy_path_from_draft_to_published(client, make_user):
    _, instructor = make_user("INSTRUCTOR")
    _, admin = make_user("ADMIN")
    course = create_course(client, instructor)
    assert course["status"] == "DRAFT"
    add_module_with_lesson(client, instructor, course["id"])

    publish(client, course_id=course["id"], author=instructor, reviewer=admin)

    detail = client.get(f"/api/v1/courses/{course['id']}", headers=admin).json()
    assert detail["status"] == "PUBLISHED"
    assert detail["published_at"] is not None
    assert detail["reviewed_by"] is not None


def test_a_course_without_modules_cannot_be_submitted(client, make_user):
    _, instructor = make_user("INSTRUCTOR")
    course = create_course(client, instructor)
    resp = client.post(f"/api/v1/courses/{course['id']}/submit-review", headers=instructor)
    assert resp.status_code == 400
    assert "at least one module" in resp.json()["detail"]


def test_instructors_cannot_approve_their_own_course(client, make_user):
    _, instructor = make_user("INSTRUCTOR")
    course = create_course(client, instructor)
    add_module_with_lesson(client, instructor, course["id"])
    client.post(f"/api/v1/courses/{course['id']}/submit-review", headers=instructor)

    resp = client.post(f"/api/v1/courses/{course['id']}/approve", headers=instructor)
    assert resp.status_code == 403


def test_requested_changes_reopen_the_course_for_editing(client, make_user):
    _, instructor = make_user("INSTRUCTOR")
    _, admin = make_user("ADMIN")
    course = create_course(client, instructor)
    add_module_with_lesson(client, instructor, course["id"])
    client.post(f"/api/v1/courses/{course['id']}/submit-review", headers=instructor)

    # Locked while in review.
    locked = client.put(f"/api/v1/courses/{course['id']}", json={"title": "Edited"}, headers=instructor)
    assert locked.status_code == 400

    resp = client.post(
        f"/api/v1/courses/{course['id']}/request-changes", json={"comment": "Add a summary lesson."}, headers=admin
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "CHANGES_REQUESTED"
    assert resp.json()["review_comment"] == "Add a summary lesson."

    edited = client.put(f"/api/v1/courses/{course['id']}", json={"title": "Edited"}, headers=instructor)
    assert edited.status_code == 200
    assert edited.json()["title"] == "Edited"


def test_only_approved_courses_can_be_published(client, make_user):
    _, instructor = make_user("INSTRUCTOR")
    _, admin = make_user("ADMIN")
    course = create_course(client, instructor)
    resp = client.post(f"/api/v1/courses/{course['id']}/publish", headers=admin)
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Only approved courses can be published."


def test_other_instructors_cannot_edit_a_course_they_do_not_own(client, make_user):
    _, owner = make_user("INSTRUCTOR")
    _, stranger = make_user("INSTRUCTOR")
    course = create_course(client, owner)
    resp = client.put(f"/api/v1/courses/{course['id']}", json={"title": "Hijacked"}, headers=stranger)
    assert resp.status_code == 403


def test_collaborators_can_edit_the_course(client, make_user):
    _, owner = make_user("INSTRUCTOR")
    collaborator_id, collaborator = make_user("INSTRUCTOR")
    course = create_course(client, owner)
    added = client.post(
        f"/api/v1/courses/{course['id']}/collaborators", json={"user_ids": [str(collaborator_id)]}, headers=owner
    )
    assert added.status_code in (200, 201)
    resp = client.post(
        f"/api/v1/courses/{course['id']}/modules", json={"title": "By collaborator"}, headers=collaborator
    )
    assert resp.status_code == 201


def test_deleting_requires_archiving_first(client, make_user):
    _, instructor = make_user("INSTRUCTOR")
    _, admin = make_user("ADMIN")
    course = create_course(client, instructor)
    add_module_with_lesson(client, instructor, course["id"])
    publish(client, course_id=course["id"], author=instructor, reviewer=admin)

    resp = client.delete(f"/api/v1/courses/{course['id']}", headers=admin)
    assert resp.status_code == 400
    assert resp.json()["detail"] == "You must archive the course before deleting it."

    assert client.post(f"/api/v1/courses/{course['id']}/archive", headers=admin).json()["status"] == "ARCHIVED"
    assert client.delete(f"/api/v1/courses/{course['id']}", headers=admin).status_code == 204
    assert client.get(f"/api/v1/courses/{course['id']}", headers=admin).status_code == 404


def test_modules_and_lessons_keep_their_order_when_moved(client, make_user):
    _, instructor = make_user("INSTRUCTOR")
    course = create_course(client, instructor)
    first = client.post(f"/api/v1/courses/{course['id']}/modules", json={"title": "First"}, headers=instructor).json()
    client.post(f"/api/v1/courses/{course['id']}/modules", json={"title": "Second"}, headers=instructor)

    resp = client.post(f"/api/v1/course-modules/{first['id']}/move", json={"direction": "down"}, headers=instructor)
    assert resp.status_code == 200, resp.text

    titles = [m["title"] for m in client.get(f"/api/v1/courses/{course['id']}", headers=instructor).json()["modules"]]
    assert titles == ["Second", "First"]

    edge = client.post(f"/api/v1/course-modules/{first['id']}/move", json={"direction": "down"}, headers=instructor)
    assert edge.status_code == 400
