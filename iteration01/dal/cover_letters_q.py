from .common import DALNotFound

def create_cover_letter(conn, cover_letter_name, user_fk, file_path, job_fk=None):
    cur = conn.execute(
        """
        INSERT INTO cover_letters (cover_letter_name, job_fk, user_fk, file_path)
        VALUES (?, ?, ?, ?)
        """,
        (cover_letter_name, job_fk, user_fk, file_path)
    )
    return cur.lastrowid

def get_cover_letter(conn, cover_id):
    return conn.execute(
        "SELECT * FROM cover_letters WHERE id = ?",
        (cover_id,)
    ).fetchone()

def list_cover_letters_by_user(conn, user_id):
    return conn.execute(
        "SELECT * FROM cover_letters WHERE user_fk = ? ORDER BY id DESC",
        (user_id,)
    ).fetchall()

def delete_cover_letter(conn, cover_id, user_id):
    cur = conn.execute(
        "DELETE FROM cover_letters WHERE id = ? AND user_fk = ?",
        (cover_id, user_id)
    )
    if cur.rowcount == 0:
        raise DALNotFound("Cover letter not found (or not owned by user).")
    
def get_latest_cover_letter_for_user(conn, user_id):
    return conn.execute(
        """
        SELECT *
        FROM cover_letters
        WHERE user_fk = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (user_id,)
    ).fetchone()

def get_cover_letter_by_name_for_user(conn, user_id, cover_letter_name):
    return conn.execute(
        """
        SELECT *
        FROM cover_letters
        WHERE user_fk = ? AND cover_letter_name = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (user_id, cover_letter_name)
    ).fetchone()