from dataclasses import dataclass

@dataclass
class Resume:
    resume_id: int
    user_id: int
    resume_name: str
    file_path: str