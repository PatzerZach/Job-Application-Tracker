from datetime import datetime

from psycopg2.errors import UniqueViolation

from .common import DALConflict


def create_user(conn, name, username, password_hash, email):
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
            row = cur.fetchone()
            return row["id"] if row else None
    except UniqueViolation as e:
        raise DALConflict(str(e))


def get_user_by_username(conn, username):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM customers WHERE lower(username) = lower(%s)",
            (username,)
        )
        return cur.fetchone()


def get_user_by_email(conn, email):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM customers WHERE lower(email) = lower(%s)",
            (email,)
        )
        return cur.fetchone()


def get_user_by_identifier(conn, identifier):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT *
            FROM customers
            WHERE lower(username) = lower(%s)
               OR lower(email) = lower(%s)
            LIMIT 1
            """,
            (identifier, identifier)
        )
        return cur.fetchone()


def get_user(conn, user_id):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM customers WHERE id = %s",
            (user_id,)
        )
        return cur.fetchone()


def mark_user_email_verified(conn, user_id):
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE customers
            SET is_verified = TRUE,
                email_verified_at = NOW()
            WHERE id = %s
            """,
            (user_id,)
        )


def update_user_password(conn, user_id, password_hash):
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE customers
            SET password = %s
            WHERE id = %s
            """,
            (password_hash, user_id)
        )


def update_user_email(conn, user_id, email):
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE customers
                SET email = %s,
                    is_verified = FALSE,
                    email_verified_at = NULL
                WHERE id = %s
                """,
                (email, user_id)
            )
    except UniqueViolation as e:
        raise DALConflict(str(e))


def delete_user_applications(conn, user_id):
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM applications WHERE user_fk = %s",
            (user_id,)
        )


def delete_user_resumes(conn, user_id):
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM resumes WHERE user_fk = %s",
            (user_id,)
        )


def delete_user_cover_letters(conn, user_id):
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM cover_letters WHERE user_fk = %s",
            (user_id,)
        )


def delete_user_account(conn, user_id):
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM customers WHERE id = %s",
            (user_id,)
        )


def create_auth_token(conn, user_id, token_hash, token_type, expires_at: datetime):
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE auth_tokens
            SET used_at = NOW()
            WHERE user_fk = %s
              AND token_type = %s
              AND used_at IS NULL
            """,
            (user_id, token_type)
        )
        cur.execute(
            """
            INSERT INTO auth_tokens (user_fk, token_hash, token_type, expires_at)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (user_id, token_hash, token_type, expires_at)
        )
        row = cur.fetchone()
        return row["id"] if row else None


def get_auth_token(conn, token_hash, token_type):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                t.id AS token_id,
                t.user_fk,
                t.token_type,
                t.expires_at,
                t.used_at,
                c.*
            FROM auth_tokens t
            JOIN customers c ON c.id = t.user_fk
            WHERE t.token_hash = %s
              AND t.token_type = %s
              AND t.used_at IS NULL
              AND t.expires_at > NOW()
            LIMIT 1
            """,
            (token_hash, token_type)
        )
        return cur.fetchone()


def mark_auth_token_used(conn, token_id):
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE auth_tokens
            SET used_at = NOW()
            WHERE id = %s
            """,
            (token_id,)
        )
