from .common import DALNotFound

def create_resume(conn, resume_name, user_fk, file_path, job_fk=None):
    cur = conn.execute(
        """
        INSERT INTO resumes (resume_name, job_fk, user_fk, file_path)
        VALUES (?, ?, ?, ?)
        """,
        (resume_name, job_fk, user_fk, file_path)
    )
    return cur.lastrowid

def get_resume(conn, resume_id):
    return conn.execute(
        "SELECT * FROM resumes WHERE id = ?",
        (resume_id,)
    ).fetchone()

def list_resumes_by_user(conn, user_id):
    return conn.execute(
        "SELECT * FROM resumes WHERE user_fk = ? ORDER BY id DESC",
        (user_id,)
    ).fetchall()

def delete_resume(conn, resume_id, user_id):
    cur = conn.execute(
        "DELETE FROM resumes WHERE id = ? AND user_fk = ?",
        (resume_id, user_id)
    )
    if cur.rowcount == 0:
        raise DALNotFound("Resume not found (or not owned by user).")
    
def get_latest_resume_for_user(conn, user_id):
    return conn.execute(
        """
        SELECT *
        FROM resumes
        WHERE user_fk = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (user_id,)
    ).fetchone()

def get_resume_by_name_for_user(conn, user_id, resume_name):
    return conn.execute(
        """
        SELECT *
        FROM resumes
        WHERE user_fk = ? AND resume_name = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (user_id, resume_name)
    ).fetchone()
    
def update_resume(conn, resume_id, resume_name, user_fk, file_path, job_fk=None):
    cur = conn.execute(
        """
        UPDATE resumes
        SET resume_name = ?, job_fk = ?, user_fk = ?, file_path = ?
        WHERE id = ?
        """,
        (resume_name, job_fk, user_fk, file_path, resume_id)
    )
    
    if cur.rowcount == 0:
        raise DALNotFound("Resume not found")
    
    return resume_id