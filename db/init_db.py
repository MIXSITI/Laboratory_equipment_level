import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "roomly.sqlite"
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"


def init_db(reset: bool = False) -> None:
    if reset and DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys = ON")
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    conn.executescript(schema_sql)
    conn.commit()

    tables = conn.execute(
        "SELECT name, type FROM sqlite_master WHERE type IN ('table', 'view')"
    ).fetchall()
    print("Созданные сущности базы данных:", tables)

    fks = conn.execute("PRAGMA foreign_key_list(bookings)").fetchall()
    print("Внешние ключи bookings:", fks)
    conn.close()


if __name__ == "__main__":
    init_db(reset=True)
