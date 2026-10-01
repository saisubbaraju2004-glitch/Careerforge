import json
import os
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.pool import NullPool
from werkzeug.security import check_password_hash, generate_password_hash

from config.config import BASE_DIR, normalize_database_url


def _database_path(database_url):
    if not isinstance(database_url, str) or not database_url.startswith("sqlite:///"):
        raise RuntimeError("DATABASE_URL must use sqlite:/// for a SQLite database.")

    raw_path = database_url[len("sqlite:///"):]
    if not raw_path:
        raise RuntimeError("DATABASE_URL must include a database path.")

    if re.match(r"^[A-Za-z]:[\\/]", raw_path):
        path = Path(raw_path)
    elif raw_path.startswith("/"):
        path = Path(raw_path)
    else:
        path = BASE_DIR / raw_path

    path.parent.mkdir(parents=True, exist_ok=True)
    return path


_engines = {}


class _DatabaseResult:
    def __init__(self, result):
        self.result = result

    @staticmethod
    def _mapping(row):
        return row._mapping if hasattr(row, "_mapping") else row

    def fetchone(self):
        row = self.result.fetchone()
        return self._mapping(row) if row is not None else None

    def fetchall(self):
        return [self._mapping(row) for row in self.result.fetchall()]

    @property
    def rowcount(self):
        return self.result.rowcount


class _DatabaseConnection:
    def __init__(self, connection, is_sqlite):
        self.connection = connection
        self.is_sqlite = is_sqlite
        self.transaction = None

    def __enter__(self):
        if not self.is_sqlite:
            self.transaction = self.connection.begin()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            if self.is_sqlite:
                return self.connection.__exit__(exc_type, exc_value, traceback)
            if exc_type is None:
                self.transaction.commit()
            else:
                self.transaction.rollback()
        finally:
            if self.is_sqlite:
                self.connection.close()
            else:
                self.connection.close()

    def execute(self, statement, parameters=()):
        if self.is_sqlite:
            return self.connection.execute(statement, parameters)

        names = [f"p{index}" for index in range(statement.count("?"))]
        if isinstance(parameters, dict):
            bound = parameters
        else:
            bound = dict(zip(names, parameters))
        sql = statement
        for name in names:
            sql = sql.replace("?", f":{name}", 1)
        sql = re.sub(r"\s+COLLATE\s+NOCASE", "", sql, flags=re.IGNORECASE)
        sql = sql.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
        sql = re.sub(r"\s+RETURNING\s+id\s*$", " RETURNING id", sql, flags=re.IGNORECASE)
        return _DatabaseResult(self.connection.execute(text(sql), bound))

    def executemany(self, statement, parameter_sets):
        if self.is_sqlite:
            return self.connection.executemany(statement, parameter_sets)
        names = [f"p{index}" for index in range(statement.count("?"))]
        sql = statement
        for name in names:
            sql = sql.replace("?", f":{name}", 1)
        sql = re.sub(r"\s+COLLATE\s+NOCASE", "", sql, flags=re.IGNORECASE)
        sql = sql.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
        bound = [dict(zip(names, values)) for values in parameter_sets]
        return _DatabaseResult(self.connection.execute(text(sql), bound))

    def executescript(self, script):
        if self.is_sqlite:
            return self.connection.executescript(script)
        for statement in script.split(";"):
            if statement.strip():
                self.connection.execute(text(statement))


def connect(database_url, serverless=None):
    database_url = normalize_database_url(database_url)
    if database_url.startswith("sqlite:///"):
        connection = sqlite3.connect(_database_path(database_url), timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 10000")
        return _DatabaseConnection(connection, is_sqlite=True)
    if not database_url.startswith("postgresql+psycopg://"):
        raise RuntimeError("DATABASE_URL must use sqlite:/// or a PostgreSQL URL.")
    engine = _database_engine(database_url, serverless)
    return _DatabaseConnection(engine.connect(), is_sqlite=False)


def _database_engine(database_url, serverless=None):
    if serverless is None:
        serverless = bool(os.getenv("VERCEL") or os.getenv("VERCEL_ENV"))
    engine_key = (database_url, bool(serverless))
    engine = _engines.get(engine_key)
    if engine is None:
        connect_args = {"connect_timeout": 10}
        if serverless:
            connect_args["prepare_threshold"] = 0
            engine = create_engine(
                database_url,
                poolclass=NullPool,
                connect_args=connect_args,
            )
        else:
            engine = create_engine(
                database_url,
                pool_pre_ping=True,
                pool_size=3,
                max_overflow=2,
                pool_timeout=20,
                pool_recycle=300,
                connect_args=connect_args,
            )
        _engines[engine_key] = engine
    return engine


def initialize_database(database_url):
    with connect(database_url) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL COLLATE NOCASE UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS user_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                category TEXT NOT NULL,
                record_id TEXT NOT NULL,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(user_id, category, record_id)
            );
            CREATE INDEX IF NOT EXISTS idx_user_records_lookup
                ON user_records(user_id, category, created_at);
            CREATE TABLE IF NOT EXISTS rate_limits (
                rate_key TEXT PRIMARY KEY,
                window_start INTEGER NOT NULL,
                request_count INTEGER NOT NULL
            );
            """
        )


def create_user(database_url, username, password):
    normalized = username.strip().lower()
    now = datetime.now(timezone.utc).isoformat()
    try:
        with connect(database_url) as connection:
            cursor = connection.execute(
                "INSERT INTO users(username, password_hash, created_at) VALUES (?, ?, ?) RETURNING id",
                (normalized, generate_password_hash(password), now),
            )
            row = cursor.fetchone()
            return {"id": row["id"], "username": normalized}
    except (sqlite3.IntegrityError, IntegrityError):
        return None


def authenticate_user(database_url, username, password):
    with connect(database_url) as connection:
        row = connection.execute(
            "SELECT id, username, password_hash FROM users WHERE username = ?",
            (username.strip().lower(),),
        ).fetchone()
    if row is None or not check_password_hash(row["password_hash"], password):
        return None
    return {"id": row["id"], "username": row["username"]}


def get_user(database_url, user_id):
    with connect(database_url) as connection:
        row = connection.execute(
            "SELECT id, username FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    return dict(row) if row else None


def set_user_record(database_url, user_id, category, record_id, payload):
    now = datetime.now(timezone.utc).isoformat()
    serialized = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    with connect(database_url) as connection:
        connection.execute(
            """
            INSERT INTO user_records(user_id, category, record_id, payload, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, category, record_id) DO UPDATE SET
                payload = excluded.payload,
                updated_at = excluded.updated_at
            """,
            (user_id, category, str(record_id), serialized, now, now),
        )


def add_user_record(database_url, user_id, category, record_id, payload):
    set_user_record(database_url, user_id, category, record_id, payload)


def get_user_records(database_url, user_id, category):
    with connect(database_url) as connection:
        rows = connection.execute(
            """
            SELECT record_id, payload, created_at, updated_at
            FROM user_records
            WHERE user_id = ? AND category = ?
            ORDER BY created_at, id
            """,
            (user_id, category),
        ).fetchall()
    return [
        {
            "id": row["record_id"],
            **json.loads(row["payload"]),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }
        for row in rows
    ]


def delete_user_record(database_url, user_id, category, record_id):
    with connect(database_url) as connection:
        cursor = connection.execute(
            "DELETE FROM user_records WHERE user_id = ? AND category = ? AND record_id = ?",
            (user_id, category, str(record_id)),
        )
    return cursor.rowcount > 0


def replace_user_records(database_url, user_id, category, records):
    now = datetime.now(timezone.utc).isoformat()
    with connect(database_url) as connection:
        connection.execute(
            "DELETE FROM user_records WHERE user_id = ? AND category = ?",
            (user_id, category),
        )
        connection.executemany(
            """
            INSERT INTO user_records(user_id, category, record_id, payload, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    user_id,
                    category,
                    str(record["id"]),
                    json.dumps(record, separators=(",", ":"), ensure_ascii=False),
                    now,
                    now,
                )
                for record in records
            ],
        )


def consume_rate_limit(database_url, rate_key, limit, window_seconds=60):
    now = int(datetime.now(timezone.utc).timestamp())
    window_start = now - now % window_seconds
    with connect(database_url) as connection:
        row = connection.execute(
            "SELECT window_start, request_count FROM rate_limits WHERE rate_key = ?",
            (rate_key,),
        ).fetchone()
        if row is None or row["window_start"] != window_start:
            connection.execute(
                """
                INSERT INTO rate_limits(rate_key, window_start, request_count)
                VALUES (?, ?, 1)
                ON CONFLICT(rate_key) DO UPDATE SET
                    window_start = excluded.window_start,
                    request_count = 1
                """,
                (rate_key, window_start),
            )
            return True, window_seconds - (now - window_start)
        if row["request_count"] >= limit:
            return False, window_seconds - (now - window_start)
        connection.execute(
            "UPDATE rate_limits SET request_count = request_count + 1 WHERE rate_key = ?",
            (rate_key,),
        )
    return True, window_seconds - (now - window_start)


def get_user_summary(database_url, user_id):
    resumes = get_user_records(database_url, user_id, "resume")
    lessons = get_user_records(database_url, user_id, "lesson")
    interviews = get_user_records(database_url, user_id, "interview")
    applications = get_user_records(database_url, user_id, "application")
    career_tasks = get_user_records(database_url, user_id, "career_task")
    latest_resume = resumes[-1] if resumes else None

    scores = [item.get("score") for item in interviews if isinstance(item.get("score"), (int, float))]
    average_interview = round(sum(scores) / len(scores)) if scores else None
    statuses = {}
    for application in applications:
        status = application.get("status", "Applied")
        statuses[status] = statuses.get(status, 0) + 1

    lesson_dates = sorted({
        item.get("completed_at", "")[:10]
        for item in lessons
        if isinstance(item.get("completed_at"), str)
    }, reverse=True)
    streak = 0
    today = datetime.now(timezone.utc).date()
    for offset, lesson_date in enumerate(lesson_dates):
        try:
            from datetime import date, timedelta
            expected = today - timedelta(days=offset)
            if date.fromisoformat(lesson_date) != expected:
                break
            streak += 1
        except ValueError:
            break

    return {
        "resume_count": len(resumes),
        "ats_score": latest_resume.get("ats_score") if latest_resume else None,
        "skills": latest_resume.get("skills", []) if latest_resume else [],
        "completed_lessons": len(lessons),
        "learning_hours": round(sum(
            float(item.get("hours", 0.5)) for item in lessons
            if isinstance(item.get("hours", 0.5), (int, float))
        ), 1),
        "learning_streak": streak,
        "interview_count": len(interviews),
        "interview_score": average_interview,
        "interviews": interviews,
        "application_count": len(applications),
        "application_statuses": statuses,
        "applications": applications,
        "career_tasks": career_tasks,
    }
