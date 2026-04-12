from .common import DALNotFound, safe_order_by

def create_resume(conn, user_id, resume_name, storage_path, original_filename=None, content_type=None):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO resumes (resume_name, user_fk, storage_path, original_filename, content_type, created_date)
            VALUES (%s, %s, %s, %s, %s, CURRENT_DATE)
            RETURNING id
            """,
            (resume_name, user_id, storage_path, original_filename, content_type)
        )
        return cur.fetchone()

def get_resume(conn, user_id, resume_id):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM resumes WHERE id = %s AND user_fk = %s",
            (resume_id, user_id)
        )
        return cur.fetchone()

def list_resumes_by_user(conn, user_id, limit=50, offset=0, sort="id", direction="DESC"):
    sort, direction = safe_order_by(sort, direction, allowed_cols={"id", "resume_name"})
    
    with conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT *
            FROM resumes
            WHERE user_fk = %s
            ORDER BY {sort} {direction}
            LIMIT %s OFFSET %s
            """,
            (user_id, limit, offset)
        )
        return cur.fetchall()

def delete_resume(conn, user_id, resume_id):
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM resumes WHERE id = %s AND user_fk = %s",
            (resume_id, user_id)
        )
        if cur.rowcount == 0:
            raise DALNotFound("Resume not found (or not owned by user).")
