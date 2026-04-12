from dal.db import connect
import re
from business.user import User
from dal.users_q import create_user, get_user_by_username, get_user, get_user_by_email
from argon2 import PasswordHasher, hash_password
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError

class AuthService:
    def __init__(self, db_path):
        self.db_path = db_path
        self.password_hasher = PasswordHasher(
            time_cost=3,
            memory_cost=65536, # 64 MiB
            parallelism=4,
            hash_len=32,
            salt_len=16,
        )

    def hash_password(self, password):
        if not isinstance(password, str) or not password:
            raise ValueError("Password must be a non-empty string")

        return self.password_hasher.hash(password)
    
    def verify_password(self, password, stored_hash):
        try:
            return self.password_hasher.verify(stored_hash, password)
        except (VerifyMismatchError, VerificationError, InvalidHashError):
            return False
    
    def verify_email(self, email):
        if not isinstance(email, str):
            raise ValueError("Email must be a string")

        email = email.strip().lower()

        if not email:
            raise ValueError("Email cannot be empty")

        email_regex = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

        if not email_regex.match(email):
            raise ValueError("Invalid email format")

        return email

    def register(self, name, username, password, email=None):
        if not name or not username or not password:
            raise ValueError("Name, Username, & Password are required")

        with connect(self.db_path) as conn:
            if email:
                email = self.verify_email(email)

                if get_user_by_email(conn, email):
                    raise ValueError("Email already exists")

            password_hash = self.hash_password(password)

            user_id = create_user(conn, name, username, password_hash, email)
            
        return user_id

    def login(self, username, password):
        if not username or not password:
            raise ValueError("Username and Password are required")

        with connect(self.db_path) as conn:
            
            row = get_user_by_username(conn, username)
            
            if row is None:
                raise ValueError("Username or password is incorrect")
            
            stored_hash = row["password"]

            if not self.verify_password(password, stored_hash):
                raise ValueError("Username or password is incorrect")

            return User(
                user_id=row["id"],
                name=row["name"],
                username=row["username"],
                email=row["email"],
                password_hash=row["password"]
            )

    def get_user_by_id(self, user_id):
        if not user_id:
            raise ValueError("User doesnt exist")

        with connect(self.db_path) as conn:
            row = get_user(conn, user_id)

            return User(
                user_id=row["id"],
                name=row["name"],
                username=row["username"],
                email=row["email"],
                password_hash=row["password"]
            )
