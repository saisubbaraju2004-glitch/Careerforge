from pathlib import Path

from services.user_store import connect, initialize_database


ROOT = Path(__file__).resolve().parents[1]


def test_supabase_migration_preserves_existing_tables_and_record_model():
    sql = (ROOT / "supabase/migrations/001_initial_schema.sql").read_text(encoding="utf-8")
    for required in (
        "public.users",
        "public.user_records",
        "public.rate_limits",
        "password_hash TEXT NOT NULL",
        "payload TEXT NOT NULL",
        "UNIQUE (user_id, category, record_id)",
    ):
        assert required in sql


def test_local_schema_bootstrap_is_sqlite_only(tmp_path):
    database = tmp_path / "careerforge.sqlite3"
    database_url = "sqlite:///" + database.as_posix()
    initialize_database(database_url)

    with connect(database_url) as connection:
        tables = {
            row["name"]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = ?", ("table",)
            ).fetchall()
        }

    assert {"users", "user_records", "rate_limits"}.issubset(tables)
