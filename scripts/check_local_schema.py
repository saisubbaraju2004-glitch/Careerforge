from pathlib import Path
from tempfile import TemporaryDirectory
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.user_store import connect, initialize_database


def main():
    with TemporaryDirectory(prefix="careerforge-schema-") as directory:
        database_file = Path(directory) / "schema-check.sqlite3"
        database_url = "sqlite:///" + database_file.as_posix()
        initialize_database(database_url)
        with connect(database_url) as connection:
            rows = connection.execute(
                "SELECT name FROM sqlite_master WHERE type = ? ORDER BY name",
                ("table",),
            ).fetchall()
        actual = {row["name"] for row in rows}
        required = {"users", "user_records", "rate_limits"}
        if not required.issubset(actual):
            raise SystemExit("Local schema bootstrap check failed.")
    print("Local SQLite schema bootstrap check passed.")


if __name__ == "__main__":
    main()
