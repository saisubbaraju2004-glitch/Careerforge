from pathlib import Path

from app import app


ROOT = Path(__file__).resolve().parents[1]


def test_flask_and_wsgi_entrypoints_expose_existing_feature_routes():
    import wsgi

    assert wsgi.app is app
    paths = {rule.rule for rule in app.url_map.iter_rules()}
    expected = {
        "/api/health",
        "/login",
        "/api/analyze-resume",
        "/api/interview-intelligence/start",
        "/api/learning/profile",
        "/api/placement-analytics/overview",
        "/api/career-os/overview",
    }
    assert expected.issubset(paths)
    assert {
        "auth",
        "career",
        "resume",
        "roadmap",
        "jobs",
        "interview",
        "applications",
        "progress",
        "intelligence",
        "career_agent",
        "placements",
        "placement_practice",
        "placement_strategy",
        "job_match",
        "interview_intelligence",
        "learning",
        "placement_analytics",
        "career_os",
    }.issubset(app.blueprints)


def test_health_checks_database_and_static_assets_are_mirrored():
    response = app.test_client().get("/api/health")
    assert response.status_code == 200
    assert response.get_json() == {
        "success": True,
        "status": "healthy",
        "database": "connected",
    }

    source_files = {
        item.relative_to(ROOT / "static")
        for item in (ROOT / "static").rglob("*")
        if item.is_file()
    }
    public_files = {
        item.relative_to(ROOT / "public" / "static")
        for item in (ROOT / "public" / "static").rglob("*")
        if item.is_file()
    }
    assert source_files == public_files
    for relative_path in source_files:
        assert (ROOT / "static" / relative_path).read_bytes() == (
            ROOT / "public" / "static" / relative_path
        ).read_bytes()


def test_health_hides_database_failure_details(monkeypatch):
    import app as app_module

    def fail_connection(database_url):
        raise RuntimeError("database password and stack details")

    monkeypatch.setattr(app_module, "connect", fail_connection)
    response = app.test_client().get("/api/health")
    assert response.status_code == 503
    assert "password" not in response.get_data(as_text=True)
    assert "stack details" not in response.get_data(as_text=True)
