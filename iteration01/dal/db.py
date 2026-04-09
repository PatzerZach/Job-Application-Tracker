import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

@contextmanager
def connect(db_url):
    conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()