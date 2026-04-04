import sqlite3
from .common import DALConflict

def create_user(conn, name, username, password_hash, email=None):
    try:
        cur = conn.execute(
            """
            INSERT INTO customers (name, username, password, email)
            VALUES (?, ?, ?, ?)
            """,
            (name, username, password_hash, email)
        )
        return cur.lastrowid
    except sqlite3.IntegrityError as e:
        raise DALConflict(str(e))

def get_user_by_username(conn, username):
    return conn.execute(
        "SELECT * FROM customers WHERE username = ?",
        (username,)
    ).fetchone()

def get_user_by_email(conn, email):
    return conn.execute(
        "SELECT * FROM customers WHERE email = ?",
        (email,)
    ).fetchone()

def get_user(conn, user_id):
    return conn.execute(
        "SELECT * FROM customers WHERE id = ?",
        (user_id,)
    ).fetchone()
