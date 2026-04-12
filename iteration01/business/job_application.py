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
    job_city: str
    job_state: str
    job_country: str
    hourly_rate: float
    salary_amount: float
    job_phone: str
    job_email: str
    resume_id: int
    cover_letter_id: int
    job_status: ApplicationStatus
    job_notes: str
    date_applied: str # TODO: str for now because sqlite doesnt have datetime
    # but when I switch to postgres, change to datetime
