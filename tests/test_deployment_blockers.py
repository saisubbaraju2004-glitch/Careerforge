import re

from app import create_app


def _client(tmp_path, username):
    database = tmp_path / f"{username}.sqlite3"
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-only-secret",
            "DATABASE_URL": f"sqlite:///{str(database).replace(chr(92), '/')}",
            "SESSION_COOKIE_SECURE": False,
            "RATE_LIMIT_AUTH": 100,
            "RATE_LIMIT_DEFAULT": 1000,
            "RATE_LIMIT_AI": 1000,
        }
    )
    client = app.test_client()
    page = client.get("/register")
    token = re.search(
        rb'name="csrf_token" value="([^"]+)"', page.data
    ).group(1).decode()
    result = client.post(
        "/register",
        data={
            "csrf_token": token,
            "username": username,
            "password": "test-password-123",
        },
    )
    assert result.status_code == 302
    return app, client


def test_user_api_requires_authentication(tmp_path):
    app, client = _client(tmp_path, "authcheck")
    anonymous = app.test_client()

    for path in ("/api/career-os/overview", "/api/placement-analytics/overview"):
        response = anonymous.get(path)
        assert response.status_code == 401
        assert response.get_json()["success"] is False

    assert client.get("/api/career-os/overview").status_code == 200


def test_v14_v15_metrics_use_private_observed_activity(tmp_path):
    _, alice = _client(tmp_path, "alice")
    _, bob = _client(tmp_path, "bobby")

    assert alice.post(
        "/api/applications",
        json={
            "applications": [
                {
                    "id": "app-1",
                    "company": "Example Co",
                    "role": "Engineer",
                    "status": "Offer",
                    "date": "2026-09-30",
                    "url": "https://example.test/jobs/1",
                }
            ]
        },
    ).status_code == 200

    assert alice.post(
        "/api/learning/complete", json={"lesson_id": "lesson-1"}
    ).status_code == 200
    assert alice.post(
        "/api/interview-intelligence/analyze",
        json={
            "question": "How would you design a test?",
            "answer": "I designed and implemented a test, measured the result, and improved the solution.",
            "expected_keywords": ["test", "designed"],
            "role": "Software Engineer",
        },
    ).status_code == 200

    funnel = alice.get("/api/placement-analytics/funnel").get_json()["data"]
    assert funnel["applications"] == 1
    assert funnel["offers"] == 1
    assert funnel["data_status"] == "observed_application_records"

    probabilities = alice.get("/api/placement-analytics/prediction").get_json()["data"]
    assert probabilities["placement_readiness_probability"] is None
    assert probabilities["data_status"] == "no_validated_prediction_model"

    overview = alice.get("/api/career-os/overview").get_json()["data"]["overview"]
    assert overview["ats_score"] is None
    assert overview["interview_score"] is not None
    assert overview["application_progress"] == 1

    bob_funnel = bob.get("/api/placement-analytics/funnel").get_json()["data"]
    bob_overview = bob.get("/api/career-os/overview").get_json()["data"]["overview"]
    assert bob_funnel["applications"] == 0
    assert bob_overview["application_progress"] == 0
    assert bob_overview["interview_score"] is None


def test_health_main_and_v12_to_v15_smoke(tmp_path):
    _, client = _client(tmp_path, "smokeuser")

    assert client.get("/api/health").status_code == 200
    assert client.get("/").status_code == 200

    get_paths = [
        "/interview-intelligence",
        "/api/interview-intelligence/history",
        "/api/interview-intelligence/readiness",
        "/learning",
        "/api/learning/profile",
        "/api/learning/progress",
        "/api/learning/resources",
        "/api/learning/next",
        "/placement-analytics",
        "/api/placement-analytics/overview",
        "/api/placement-analytics/prediction",
        "/api/placement-analytics/companies",
        "/api/placement-analytics/funnel",
        "/api/placement-analytics/trends",
        "/api/placement-analytics/risks",
        "/api/placement-analytics/goals",
        "/career-os",
        "/api/career-os/overview",
        "/api/career-os/report",
        "/api/career-os/search?q=python",
    ]
    for path in get_paths:
        response = client.get(path)
        assert response.status_code == 200, f"{path}: HTTP {response.status_code}"
        if path.startswith("/api/"):
            assert response.is_json and response.get_json()["success"] is True, path

    start = client.post(
        "/api/interview-intelligence/start", json={"role": "Backend Engineer"}
    )
    assert start.status_code == 200
    session_id = start.get_json()["data"]["session_id"]
    answer = client.post(
        "/api/interview-intelligence/analyze",
        json={
            "session_id": session_id,
            "question": "How do you test a service?",
            "answer": "I designed a test, implemented it, and measured the result.",
            "expected_keywords": ["test", "measured"],
        },
    )
    assert answer.status_code == 200
    assert client.post(
        "/api/learning/complete", json={"lesson_id": "smoke-lesson"}
    ).status_code == 200
    assert client.post(
        "/api/career-os/action",
        json={"task_id": "smoke-task", "completed": True},
    ).status_code == 200
    assert client.post(
        "/api/career-os/chat", json={"message": "What is my progress?"}
    ).status_code == 200
