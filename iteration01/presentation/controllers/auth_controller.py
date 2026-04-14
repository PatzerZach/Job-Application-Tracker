class AuthController:
    def __init__(self, auth_service):
        self.auth_service = auth_service

    def login(self, identifier, password):
        return self.auth_service.login(identifier, password)

    def register(self, name, username, password, email, confirm_email, base_url):
        return self.auth_service.register(name, username, password, email, confirm_email, base_url)

    def request_password_reset(self, email, base_url):
        return self.auth_service.request_password_reset(email, base_url)

    def reset_password(self, token, password, confirm_password, base_url):
        return self.auth_service.reset_password(token, password, confirm_password, base_url)

    def verify_email_token(self, token):
        return self.auth_service.verify_email_token(token)

    def resend_verification(self, user_id, base_url):
        return self.auth_service.resend_verification(user_id, base_url)

    def change_password(self, user_id, current_password, new_password, confirm_password, base_url):
        return self.auth_service.change_password(user_id, current_password, new_password, confirm_password, base_url)

    def change_email(self, user_id, email, confirm_email, base_url):
        return self.auth_service.change_email(user_id, email, confirm_email, base_url)

    def delete_account(self, user_id, current_password):
        return self.auth_service.delete_account(user_id, current_password)

    def get_user(self, user_id):
        return self.auth_service.get_user_by_id(user_id)
