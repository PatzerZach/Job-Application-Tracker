from dataclasses import dataclass

@dataclass
class Resume:
    resume_id: int
    user_id: int
    resume_name: str
    storage_path: str
    original_filename: str
    content_type: str