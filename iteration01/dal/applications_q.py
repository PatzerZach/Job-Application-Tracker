from .common import DALNotFound, safe_order_by

ALLOWED_APPLICATION_UPDATE_COLUMNS = {
    "job_title",
    "job_company",
    "job_name",
    "job_description",
    "job_city",
    "job_state",
    "job_country",
    "hourly_rate",
    "salary_amount",
    "job_phone",
    "job_email",
    "resume_fk",
    "cover_letter_fk",
    "job_status",
    "job_notes",
    "date_applied"
}

def create_application(conn, user_fk, date_applied, job_title, job_company=None, job_name=None, job_description=None, job_city=None,
                       job_state=None, job_country="United States", hourly_rate=None, salary_amount=None, job_phone=None,
                       job_email=None, resume_fk=None, cover_letter_fk=None, job_status=None, job_notes=None):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO applications (
                user_fk,
                job_title,
                job_company,
                job_name,
                job_description,
                job_city,
                job_state,
                job_country,
                hourly_rate,
                salary_amount,
                job_phone,
                job_email,
                resume_fk,
                cover_letter_fk,
                job_status,
                job_notes,
                date_applied,
                created_date
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_DATE)
            RETURNING id
            """,
            (
                user_fk,
                job_title,
                job_company,
                job_name,
                job_description,
                job_city,
                job_state,
                job_country,
                hourly_rate,
                salary_amount,
                job_phone,
                job_email,
                resume_fk,
                cover_letter_fk,
                job_status,
                job_notes,
                date_applied,
            )
        )
        return cur.fetchone()


def update_application(conn, app_id, user_id, updates):
    if not updates:
        raise ValueError("No updates provided")
    
    invalid_cols = set(updates.keys()) - ALLOWED_APPLICATION_UPDATE_COLUMNS
    if invalid_cols:
        raise ValueError(f"Invalid update columns: {invalid_cols}")
    
    set_clause=", ".join(f"{column} = %s" for column in updates.keys())
    values = list(updates.values())
    
    with conn.cursor() as cur:
        cur.execute(
            f"""
            UPDATE applications
            SET {set_clause}
            WHERE id = %s AND user_fk = %s
            """,
            (*values, app_id, user_id)
        )

        if cur.rowcount == 0:
            raise DALNotFound("Application not found (or not owned by user).")

def get_application(conn, app_id):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM applications WHERE id = %s",
            (app_id,)
        )
        return cur.fetchone()


# Not Needed for onw

# def get_application_detail(conn, app_id):
#     # join to show the resume and cover letter info for this application
#     return conn.execute(
#         """
#         SELECT
#           a.id AS application_id,
#           a.job_name,
#           a.user_fk,
#           r.id AS resume_id,
#           r.resume_name,
#           r.file_path AS resume_file_path,
#           c.id AS cover_letter_id,
#           c.cover_letter_name,
#           c.file_path AS cover_file_path
#         FROM applications a
#         JOIN resumes r ON r.id = a.resume_fk
#         LEFT JOIN cover_letters c ON c.id = a.cover_letter_fk
#         WHERE a.id = %s
#         """,
#         (app_id,)
#     ).fetchone()

def list_applications_by_user(conn, user_id, limit=50, offset=0, sort="id", direction="DESC"):
    sort, direction = safe_order_by(sort, direction, allowed_cols={"id", "job_name"})

    with conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT *
            FROM applications
            WHERE user_fk = %s
            ORDER BY {sort} {direction}
            LIMIT %s OFFSET %s
            """,
            (user_id, limit, offset)
        )
        return cur.fetchall()

def delete_application(conn, app_id, user_id):
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM applications WHERE id = %s AND user_fk = %s",
            (app_id, user_id)
        )
        if cur.rowcount == 0:
            raise DALNotFound("Application not found (or not owned by user).")
