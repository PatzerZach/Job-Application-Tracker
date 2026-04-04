from business.application_service import ApplicationService

class ApplicationController:
    def __init__(self, application_service):
        self.application_service = application_service

    def create_application(self, user_id, job_title, job_company=None, job_name=None, job_description=None, job_phone=None, 
                           job_email=None, resume_id=None, cover_letter_id=None):
        return self.application_service.create_application(
            user_id, job_title, job_company, job_name, job_description, job_phone, job_email, resume_id, cover_letter_id
        )
        
    def update_application(self, app_id, user_id, job_title=None, job_company=None, job_name=None, job_description=None, job_phone=None,
                           job_email=None, resume_id=None, cover_letter_id=None, job_status=None):
        return self.application_service.update_application(
            app_id, user_id, job_title, job_company, job_name, job_description, job_phone, job_email, resume_id, cover_letter_id, job_status
        )
        
    def delete_application(self, app_id, user_id):
        return self.application_service.delete_application(app_id, user_id)
    
    def list_applications(self, user_id):
        return self.application_service.list_applications(user_id)
    
    def set_status(self, app_id, user_id, job_status):
        return self.application_service.set_status(app_id, user_id, job_status)
    
    def get_application(self, app_id, user_id):
        return self.application_service.get_application(app_id, user_id)
