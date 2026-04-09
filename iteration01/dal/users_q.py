from psycopg.errors import UniqueViolation
from .common import DALConflict

def create_user(conn, name, username, password_hash, email=None):
    
    try:
        return conn.execute(
            """
            INSERT INTO customers (name, username, password, email, created_date)
            VALUES (%s, %s, %s, %s, CURRENT_DATE)
            RETURNING id
            """,
            (name, username, password_hash, email)
        ).fetchone()
    except UniqueViolation as e:
        raise DALConflict(str(e))

def get_user_by_username(conn, username):
    return conn.execute(
        "SELECT * FROM customers WHERE username = %s",
        (username,)
    ).fetchone()

def get_user_by_email(conn, email):
    return conn.execute(
        "SELECT * FROM customers WHERE email = %s",
        (email,)
    ).fetchone()

def get_user(conn, user_id):
    return conn.execute(
        "SELECT * FROM customers WHERE id = %s",
        (user_id,)
    ).fetchone()
