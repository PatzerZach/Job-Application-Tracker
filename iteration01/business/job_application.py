from dataclasses import dataclass
from business.application_status import ApplicationStatus

@dataclass
class JobApplication:
    application_id: int
    user_id: int
    job_company: str
    job_name: str
    job_title: str
    job_description: str
    job_phone: int
    job_email: str
    resume_id: int
    cover_letter_id: int
    job_status: ApplicationStatus