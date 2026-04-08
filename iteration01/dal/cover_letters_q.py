from .common import DALNotFound, safe_order_by
from datetime import date

def create_cover_letter(conn, user_id, cover_letter_name, storage_path, original_filename=None, content_type=None):
    created_at = date.today().isoformat()

    cur = conn.execute(
        """
        INSERT INTO cover_letters (cover_letter_name, user_fk, storage_path, original_filename, content_type, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (cover_letter_name, user_id, storage_path, original_filename, content_type, created_at)
    )
    return cur.lastrowid

def get_cover_letter(conn, user_id, cover_letter_id):
    return conn.execute(
        "SELECT * FROM cover_letters WHERE id = ? AND user_fk = ?",
        (cover_id, user_id)
    ).fetchone()

def list_cover_letters_by_user(conn, user_id, limit=50, offset=0, sort="id", direction="DESC"):
    sort, direction = safe_order_by(sort, direction, allowed_cols={"id", "cover_letter_name"})

    return conn.execute(
        f"""
        SELECT *
        FROM cover_letters
        WHERE user_fk = ?
        ORDER BY {sort} {direction}
        LIMIT ? OFFSET ?
        """,
        (user_id, limit, offset)
    ).fetchall()

def delete_cover_letter(conn, user_id, cover_letter_id):
    cur = conn.execute(
        "DELETE FROM cover_letters WHERE id = ? AND user_fk = ?",
        (cover_letter_id, user_id)
    )
    if cur.rowcount == 0:
        raise DALNotFound("Cover letter not found (or not owned by user).")
