from .common import DALNotFound, safe_order_by

def create_cover_letter(conn, user_id, cover_letter_name, storage_path, original_filename=None, content_type=None):

    return conn.execute(
        """
        INSERT INTO cover_letters (cover_letter_name, user_fk, storage_path, original_filename, content_type, created_date)
        VALUES (%s, %s, %s, %s, %s, CURRENT_DATE)
        RETURNING id
        """,
        (cover_letter_name, user_id, storage_path, original_filename, content_type)
    ).fetchone()

def get_cover_letter(conn, user_id, cover_letter_id):
    return conn.execute(
        "SELECT * FROM cover_letters WHERE id = %s AND user_fk = %s",
        (cover_letter_id, user_id)
    ).fetchone()

def list_cover_letters_by_user(conn, user_id, limit=50, offset=0, sort="id", direction="DESC"):
    sort, direction = safe_order_by(sort, direction, allowed_cols={"id", "cover_letter_name"})

    return conn.execute(
        f"""
        SELECT *
        FROM cover_letters
        WHERE user_fk = %s
        ORDER BY {sort} {direction}
        LIMIT %s OFFSET %s
        """,
        (user_id, limit, offset)
    ).fetchall()

def delete_cover_letter(conn, user_id, cover_letter_id):
    cur = conn.execute(
        "DELETE FROM cover_letters WHERE id = %s AND user_fk = %s",
        (cover_letter_id, user_id)
    )
    if cur.rowcount == 0:
        raise DALNotFound("Cover letter not found (or not owned by user).")
