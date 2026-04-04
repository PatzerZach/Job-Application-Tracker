from dal.db import connect
from business.application_status import ApplicationStatus
from business.job_application import JobApplication
from dal.applications_q import create_application, update_application, delete_application, get_application, list_applications_by_user

class ApplicationService:
    def __init__(self, db_path):
        self.db_path = db_path

    def create_application(self, user_id, date_applied, job_title, job_company=None, job_name=None, job_description=None, job_phone=None,
                           job_email=None, resume_id=None, cover_letter_id=None, job_notes=None):
        if not job_title:
            raise ValueError("Job Title is required")
        
        if not date_applied:
            raise ValueError("Date Applied required")

        # Grabbing the integer value of NOT_APPLIED from the enum which is 0
        status = ApplicationStatus.NOT_APPLIED.value

        with connect(self.db_path) as conn:
            return create_application(
                conn=conn,
                user_fk=user_id,
                date_applied=date_applied,
                job_title=job_title,
                job_company=job_company,
                job_name=job_name,
                job_description=job_description,
                job_phone=job_phone,
                job_email=job_email,
                resume_fk=resume_id,
                cover_letter_fk=cover_letter_id,
                job_status=status,
                job_notes=job_notes
            )

    def update_application(self, app_id, user_id, job_title=None, job_company=None, job_name=None, job_description=None, job_phone=None,
                           job_email=None, resume_fk=None, cover_letter_fk=None, job_status=None, job_notes=None, date_applied=None):
        updates = {}

        field_map = {
            "job_title" : job_title,
            "job_company" : job_company,
            "job_name" : job_name,
            "job_description" : job_description,
            "job_phone" : job_phone,
            "job_email" : job_email,
            "resume_fk" : resume_fk,
            "cover_letter_fk" : cover_letter_fk,
            "job_notes" : job_notes,
            "date_applied" : date_applied
        }
        
        for field, value in field_map.items():
            if value is not None:
                updates[field] = value
                
        if job_status is not None:
            if isinstance(job_status, ApplicationStatus):
                updates["job_status"] = job_status.value
            else:
                updates["job_status"] = job_status

        if not updates:
            raise ValueError("At least one field must be provided for update.")
        
        with connect(self.db_path) as conn:
            update_application(conn, app_id, user_id, updates)

        return True

    def delete_application(self, app_id, user_id):
        with connect(self.db_path) as conn:
            delete_application(conn, app_id, user_id)

        return True

    def _row_to_job_application(self, row):
        return JobApplication(
                application_id=row["id"],
                user_id=row["user_fk"],
                job_company=row["job_company"],
                job_name=row["job_name"],
                job_title=row["job_title"],
                job_description=row["job_description"],
                job_phone=row["job_phone"],
                job_email=row["job_email"],
                resume_id=row["resume_fk"],
                cover_letter_id=row["cover_letter_fk"],
                job_status=ApplicationStatus(row["job_status"]),
                job_notes=row["job_notes"],
                date_applied=row["date_applied"]
        )


    def get_application(self, app_id, user_id):
        with connect(self.db_path) as conn:
            row = get_application(conn, app_id)

            if row is None:
                return None

            if user_id is not None and row["user_fk"] != user_id:
                return None
            
            # Call helper method
            return self._row_to_job_application(row)

            
    def list_applications(self, user_id):
        with connect(self.db_path) as conn:
            rows = list_applications_by_user(conn, user_id)
            
            # Call helper method and create JobApplication object for each row. Store each object in a list and return it
            return [self._row_to_job_application(row) for row in rows]


    def set_status(self, app_id, user_id, job_status):
        if not isinstance(job_status, ApplicationStatus):
            raise ValueError("Invalid Status")

        with connect(self.db_path) as conn:
            update_application(conn, app_id, user_id, {"job_status": job_status.value})

        return True
