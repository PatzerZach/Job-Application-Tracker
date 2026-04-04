from business.auth_service import AuthService

class AuthController:
    
    def __init__(self, auth_service):
        self.auth_service = auth_service

    def login(self, username, password):
        return self.auth_service.login(username, password)

    def register(self, name, username, password, email=None):
        return self.auth_service.register(name, username, password, email)

    def get_user(self, user_id):
        return self.auth_service.get_user_by_id(user_id)
