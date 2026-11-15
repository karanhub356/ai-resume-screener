"""Database initialization and connection management."""
import os
import sqlite3
from pathlib import Path

DB_PATH = os.environ.get("DATABASE_PATH", "./resume_screener.db")
SCHEMA_FILE = Path(__file__).parent / "schema.sql"

def get_db_connection():
    """Get database connection with foreign keys enabled."""
    parent = Path(DB_PATH).parent
    if str(parent) not in ("", "."):
        parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Initialize database schema if tables don't exist."""
    try:
        if SCHEMA_FILE.exists():
            with get_db_connection() as conn:
                conn.executescript(SCHEMA_FILE.read_text(encoding='utf-8'))
    except Exception as e:
        print(f"Warning: Database initialization issue: {e}")
