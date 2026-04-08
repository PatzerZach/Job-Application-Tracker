from dataclasses import dataclass

@dataclass
class CoverLetter:
    cover_letter_id: int
    user_id: int
    cover_letter_name: str
    storage_path: str
    original_filename: str
    content_type: str
