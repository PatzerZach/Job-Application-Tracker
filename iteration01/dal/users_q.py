from psycopg2.errors import UniqueViolation
from .common import DALConflict

def create_user(conn, name, username, password_hash, email=None):
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO customers (name, username, password, email, created_date)
                VALUES (%s, %s, %s, %s, CURRENT_DATE)
                RETURNING id
                """,
                (name, username, password_hash, email)
            )
            return cur.fetchone()
    except UniqueViolation as e:
        raise DALConflict(str(e))

def get_user_by_username(conn, username):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM customers WHERE username = %s",
            (username,)
        )
        return cur.fetchone()

def get_user_by_email(conn, email):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM customers WHERE email = %s",
            (email,)
        )
        return cur.fetchone()

def get_user(conn, user_id):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM customers WHERE id = %s",
            (user_id,)
        )
        return cur.fetchone()
