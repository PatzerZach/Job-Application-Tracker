from .common import DALNotFound, safe_order_by

ALLOWED_APPLICATION_UPDATE_COLUMNS = {
    "job_title",
    "job_company",
    "job_name",
    "job_description",
    "job_phone",
    "job_email",
    "resume_fk",
    "cover_letter_fk",
    "job_status",
    "job_notes",
    "date_applied"
}

def create_application(conn, user_fk, date_applied, job_title, job_company=None, job_name=None, job_description=None, job_phone=None, job_email=None, resume_fk=None, cover_letter_fk=None, job_status=None, job_notes=None):
    cur = conn.execute(
        """
        INSERT INTO applications (
            user_fk,
            job_title,
            job_company,
            job_name,
            job_description,
            job_phone,
            job_email,
            resume_fk,
            cover_letter_fk,
            job_status,
            job_notes,
            date_applied
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (user_fk, job_title, job_company, job_name, job_description, job_phone, job_email, resume_fk, cover_letter_fk, job_status, job_notes, date_applied)
    )
    return cur.lastrowid


def update_application(conn, app_id, user_id, updates):
    if not updates:
        raise ValueError("No updates provided")
    
    invalid_cols = set(updates.keys()) - ALLOWED_APPLICATION_UPDATE_COLUMNS
    if invalid_cols:
        raise ValueError(f"Invalid update columns: {invalid_cols}")
    
    set_clause=", ".join(f"{column} = ?" for column in updates.keys())
    values = list(updates.values())
    
    cur = conn.execute(
        f"""
        UPDATE applications
        SET {set_clause}
        WHERE id = ? AND user_fk = ?
        """,
        (*values, app_id, user_id)
    )
    
    if cur.rowcount == 0:
        raise DALNotFound("Application not found (or not owned by user).")

def get_application(conn, app_id):
    return conn.execute(
        "SELECT * FROM applications WHERE id = ?",
        (app_id,)
    ).fetchone()

def get_application_detail(conn, app_id):
    # join to show the resume and cover letter info for this application
    return conn.execute(
        """
        SELECT
          a.id AS application_id,
          a.job_name,
          a.user_fk,
          r.id AS resume_id,
          r.resume_name,
          r.file_path AS resume_file_path,
          c.id AS cover_letter_id,
          c.cover_letter_name,
          c.file_path AS cover_file_path
        FROM applications a
        JOIN resumes r ON r.id = a.resume_fk
        LEFT JOIN cover_letters c ON c.id = a.cover_letter_fk
        WHERE a.id = ?
        """,
        (app_id,)
    ).fetchone()

def list_applications_by_user(conn, user_id, limit=50, offset=0, sort="id", direction="DESC"):
    sort, direction = safe_order_by(sort, direction, allowed_cols={"id", "job_name"})

    return conn.execute(
        f"""
        SELECT *
        FROM applications
        WHERE user_fk = ?
        ORDER BY {sort} {direction}
        LIMIT ? OFFSET ?
        """,
        (user_id, limit, offset)
    ).fetchall()

def delete_application(conn, app_id, user_id):
    cur = conn.execute(
        "DELETE FROM applications WHERE id = ? AND user_fk = ?",
        (app_id, user_id)
    )
    if cur.rowcount == 0:
        raise DALNotFound("Application not found (or not owned by user).")
