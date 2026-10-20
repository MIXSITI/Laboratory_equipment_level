import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "roomly.sqlite"


def get_connection() -> sqlite3.Connection:
    """Create and configure a SQLite connection with foreign key support."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
