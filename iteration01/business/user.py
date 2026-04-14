from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    user_id: int
    name: str
    username: str
    email: str
    password_hash: str
    is_verified: bool = False
    email_verified_at: datetime | None = None
