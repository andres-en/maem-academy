"""JWT authentication and role-based access control."""

from __future__ import annotations

import uuid

import pytest

from app.core.security import create_access_token


def test_health_and_system_info_are_public(client):
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/api/v1/system/info").json()["google_oauth_enabled"] is False


@pytest.mark.parametrize("path", ["/api/v1/auth/me", "/api/v1/courses", "/api/v1/users", "/api/v1/enrollments/me"])
def test_requests_without_a_token_are_rejected(client, path):
    resp = client.get(path)
    assert resp.status_code == 401
    assert resp.json() == {"detail": "Not authenticated."}


def test_tampered_or_foreign_tokens_are_rejected(client):
    assert client.get("/api/v1/auth/me", headers={"Authorization": "Bearer not-a-jwt"}).status_code == 401
    ghost = create_access_token(subject=str(uuid.uuid4()))
    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {ghost}"})
    assert resp.status_code == 401
    assert resp.json() == {"detail": "User not found."}


def test_inactive_user_is_forbidden(client, make_user):
    _, headers = make_user("USER", status="INACTIVE")
    resp = client.get("/api/v1/auth/me", headers=headers)
    assert resp.status_code == 403
    assert resp.json() == {"detail": "User is inactive."}


def test_me_returns_the_authenticated_user(client, make_user):
    _, headers = make_user("INSTRUCTOR", email="teacher@example.com")
    body = client.get("/api/v1/auth/me", headers=headers).json()
    assert body["email"] == "teacher@example.com"
    assert body["role"]["name"] == "INSTRUCTOR"


def test_google_login_is_rejected_when_oauth_is_not_configured(client):
    resp = client.post("/api/v1/auth/google", json={"id_token": "fake"})
    assert resp.status_code == 401


@pytest.mark.parametrize(
    "method, path",
    [
        ("get", "/api/v1/users"),
        ("post", "/api/v1/groups"),
        ("post", "/api/v1/categories"),
        ("get", "/api/v1/reports/summary"),
        ("post", "/api/v1/courses"),
    ],
)
def test_learners_cannot_reach_management_endpoints(client, make_user, method, path):
    _, learner = make_user("USER")
    resp = getattr(client, method)(
        path, headers=learner, **({"json": {"name": "x", "title": "x"}} if method == "post" else {})
    )
    assert resp.status_code == 403
    assert resp.json() == {"detail": "You do not have permission for this action."}


def test_instructors_can_author_courses_and_search_users_but_not_manage_them(client, make_user):
    _, instructor = make_user("INSTRUCTOR")
    assert client.post("/api/v1/courses", json={"title": "Intro"}, headers=instructor).status_code == 201
    # Instructors search the directory to add course collaborators...
    assert client.get("/api/v1/users", headers=instructor).status_code == 200
    # ...but cannot create or edit users.
    new_user = {"full_name": "X", "email": "x@example.com", "role_id": "00000000-0000-0000-0000-000000000000"}
    assert client.post("/api/v1/users", json=new_user, headers=instructor).status_code == 403


def test_learners_cannot_browse_the_user_directory(client, make_user):
    """Regression: any authenticated learner could list every user's name, email and role."""
    staff_id, _ = make_user("ADMIN")
    _, learner = make_user("USER")
    assert client.get("/api/v1/users", headers=learner).status_code == 403
    assert client.get(f"/api/v1/users/{staff_id}", headers=learner).status_code == 403
