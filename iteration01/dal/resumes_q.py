from .common import DALNotFound, safe_order_by
from datetime import date

def create_resume(conn, user_id, resume_name, storage_path, original_filename=None, content_type=None):
    
    created_at = date.today().isoformat()

    cur = conn.execute(
        """
        INSERT INTO resumes (resume_name, user_fk, storage_path, original_filename, content_type, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (resume_name, user_id, storage_path, original_filename, content_type, created_at)
    )
    return cur.lastrowid

def get_resume(conn, user_id, resume_id):
    return conn.execute(
        "SELECT * FROM resumes WHERE id = ? AND user_fk = ?",
        (resume_id, user_id)
    ).fetchone()

def list_resumes_by_user(conn, user_id, limit=50, offset=0, sort="id", direction="DESC"):
    sort, direction = safe_order_by(sort, direction, allowed_cols={"id", "resume_name"})
    
    return conn.execute(
        f"""
        SELECT *
        FROM resumes
        WHERE user_fk = ?
        ORDER BY {sort} {direction}
        LIMIT ? OFFSET ?
        """,
        (user_id, limit, offset)
    ).fetchall()

def delete_resume(conn, user_id, resume_id):
    cur = conn.execute(
        "DELETE FROM resumes WHERE id = ? AND user_fk = ?",
        (resume_id, user_id)
    )
    if cur.rowcount == 0:
        raise DALNotFound("Resume not found (or not owned by user).")