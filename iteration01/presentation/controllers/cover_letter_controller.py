from business.cover_letter_service import CoverLetterService

class CoverLetterController:
    def __init__(self, cover_letter_service):
        self.cover_letter_service = cover_letter_service

    def create_cover_letter(self, user_id, cover_letter_name, file_bytes, original_filename=None, content_type=None):
       return self.cover_letter_service.create_cover_letter(user_id, cover_letter_name, file_bytes, original_filename, content_type)

    def list_cover_letters(self, user_id):
        return self.cover_letter_service.list_cover_letters(user_id)

    def get_cover_letter(self, user_id, cover_letter_id):
        return self.cover_letter_service.get_cover_letter(user_id, cover_letter_id)

    def delete_cover_letter(self, user_id, cover_letter_id):
        return self.cover_letter_service.delete_cover_letter(user_id, cover_letter_id)

    def get_cover_letter_download_url(self, user_id, cover_letter_id, expires_in=3600):
        return self.cover_letter_service.get_cover_letter_download_url(user_id, cover_letter_id, expires_in)
