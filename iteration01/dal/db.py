import sqlite3
from contextlib import contextmanager

@contextmanager
def connect(db_path):
    conn = sqlite3.connect(db_path)
    try:
        conn.row_factory = sqlite3.Row

        # Force foreign keys otherwise SQLite ignores foreign keys
        conn.execute("PRAGMA foreign_keys = ON;")

        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()