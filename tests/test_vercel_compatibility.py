from sqlalchemy.pool import NullPool

import config.config as config
from services import user_store


def test_vercel_database_url_is_selected_and_normalized(monkeypatch):
    monkeypatch.setattr(config, "IS_VERCEL", True)
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://app:local-test@pooler.invalid:6543/postgres",
    )

    selected = config._database_url_from_environment()

    assert selected.startswith("postgresql+psycopg://app:local-test@pooler.invalid:6543/")
    assert "sslmode=require" in selected


def test_vercel_engine_uses_null_pool_and_disables_prepare(monkeypatch):
    database_url = config.normalize_database_url(
        "postgresql://app:local-test@pooler.invalid:6543/postgres"
    )
    real_create_engine = user_store.create_engine
    captured = {}

    def capture_engine_options(url, **kwargs):
        captured.update(kwargs)
        return real_create_engine(url, **kwargs)

    monkeypatch.setattr(user_store, "_engines", {})
    monkeypatch.setattr(user_store, "create_engine", capture_engine_options)
    engine = user_store._database_engine(database_url, serverless=True)

    assert isinstance(engine.pool, NullPool)
    assert captured["poolclass"] is NullPool
    assert captured["connect_args"]["prepare_threshold"] == 0
    assert captured["connect_args"]["connect_timeout"] == 10
