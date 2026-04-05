from business.resume_service import ResumeService

class ResumeController:
    def __init__(self, resume_service):
        self.resume_service = resume_service

    def create_resume(self, user_id, resume_name, file_bytes, original_filename=None, content_type=None):
        return self.resume_service.create_resume(user_id, resume_name, file_bytes, original_filename, content_type)

    def list_resumes(self, user_id):
        return self.resume_service.list_resumes(user_id)

    def get_resume(self, user_id, resume_id):
        return self.resume_service.get_resume(user_id, resume_id)

    def delete_resume(self, user_id, resume_id):
        return self.resume_service.delete_resume(user_id, resume_id)
