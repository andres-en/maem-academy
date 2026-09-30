"""The generated OpenAPI document is complete enough to be used as API documentation."""

from __future__ import annotations

from app.main import OPENAPI_TAGS, app


def test_every_operation_is_tagged_with_a_documented_tag():
    documented = {t["name"] for t in OPENAPI_TAGS}
    for path, item in app.openapi()["paths"].items():
        for method, op in item.items():
            assert op.get("tags"), f"{method.upper()} {path} has no tag"
            assert set(op["tags"]) <= documented, f"{method.upper()} {path} uses an undocumented tag"


def test_protected_operations_declare_the_bearer_scheme():
    public = {
        ("/health", "get"),
        ("/api/v1/system/info", "get"),
        ("/api/v1/auth/google", "post"),
        ("/api/v1/users/import/template", "get"),
    }
    for path, item in app.openapi()["paths"].items():
        for method, op in item.items():
            if (path, method) in public:
                continue
            assert op.get("security"), f"{method.upper()} {path} does not declare authentication"


def test_docs_are_served(client):
    assert client.get("/docs").status_code == 200
    assert client.get("/openapi.json").json()["info"]["title"] == "MAEM Academy API"
