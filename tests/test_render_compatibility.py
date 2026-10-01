from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_render_blueprint_uses_supabase_supplied_database_url():
    render_yaml = (ROOT / "render.yaml").read_text(encoding="utf-8")

    assert "name: CareerForge" in render_yaml
    assert "branch: master" in render_yaml
    assert "runtime: python" in render_yaml
    assert "buildCommand: pip install -r requirements.txt" in render_yaml
    assert "startCommand: gunicorn --bind 0.0.0.0:$PORT wsgi:app" in render_yaml
    assert "healthCheckPath: /api/health" in render_yaml
    assert "fromGroup: careerforge-production" in render_yaml
    assert "key: DATABASE_URL\n        sync: false" in render_yaml
    assert "fromDatabase:" not in render_yaml
    assert "databases:" not in render_yaml
    assert "FLASK_SECRET_KEY" not in render_yaml
    assert "FLASK_SECRET_KEY_2" not in render_yaml
