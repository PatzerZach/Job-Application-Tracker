import os
import uuid

from dal.db import connect
from dal.cover_letters_q import create_cover_letter, delete_cover_letter, get_cover_letter, list_cover_letters_by_user
from business.cover_letter import CoverLetter

class CoverLetterService:
    def __init__(self, db_path, storage_service):
        self.db_path = db_path
        self.storage_service = storage_service

    def _row_to_cover_letter(self, row):
        return CoverLetter(
            cover_letter_id=row["id"],
            user_id=row["user_fk"],
            cover_letter_name=row["cover_letter_name"],
            storage_path=row["storage_path"],
            original_filename=row["original_filename"],
            content_type=row["content_type"]
        )

    def create_cover_letter(self, user_id, cover_letter_name, file_bytes, original_filename, content_type):
        if not user_id:
            raise ValueError("User ID is required")

        if not cover_letter_name or not cover_letter_name.strip():
            raise ValueError("Cover Letter name is required")

        if not file_bytes:
            raise ValueError("Uploaded file is required")

        if not original_filename:
            raise ValueError("Original filename is required")

        allowed_types = {
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        }

        if content_type not in allowed_types:
            raise ValueError("Invalid file type. Only PDF, DOC, DOCX are allowed")

        safe_cover_letter_name = cover_letter_name.strip()
        extension = os.path.splitext(original_filename)[1].lower()
        unique_name = f"{uuid.uuid4()}{extension}"
        storage_path = f"{user_id}/{unique_name}"

        stored_path = self.storage_service.upload_file(bucket_name="cover_letters", storage_path=storage_path, file_bytes=file_bytes, content_type=content_type)
        
        with connect(self.db_path) as conn:
            cover_letter_id = create_cover_letter(
                conn=conn,
                user_id=user_id,
                cover_letter_name=cover_letter_name,
                storage_path=stored_path,
                original_filename=original_filename,
                content_type=content_type
            )

        return cover_letter_id

    def get_cover_letter(self, user_id, cover_letter_id):
        if not user_id or not cover_letter_id:
            raise ValueError("User_id and cover_letter_id are required")

        with connect(self.db_path) as conn:
            row = get_cover_letter(conn, user_id, cover_letter_id)

        if row is None:
            return None

        return self._row_to_cover_letter(row)

    def list_cover_letters(self, user_id, limit=50, offset=0, sort="id", direction="DESC"):
        if not user_id:
            raise ValueError("User_id is required")

        with connect(self.db_path) as conn:
            rows = list_cover_letters_by_user(conn, user_id, limit, offset, sort, direction)

        return [self._row_to_cover_letter(row) for row in rows]

    def delete_cover_letter(self, user_id, cover_letter_id):
        if not user_id or not cover_letter_id:
            raise ValueError("User_id and Cover_letter_id are required")

        with connect(self.db_path) as conn:
            row = get_cover_letter(conn, user_id, cover_letter_id)

            if row is None:
                raise ValueError("Cover Letter not found")

            storage_path = row["storage_path"]

            self.storage_service.delete_file(bucket_name="cover_letters", storage_path=storage_path)

            delete_cover_letter(conn, user_id, cover_letter_id)

        return True

    def get_cover_letter_download_url(self, user_id, cover_letter_id, expires_in=3600):
        if not user_id or not cover_letter_id:
            raise ValueError("User_id and Cover_letter_id are required")

        with connect(self.db_path) as conn:
            row = get_cover_letter(conn, user_id, cover_letter_id)

            if row is None:
                raise ValueError("Cover Letter not found")

            return self.storage_service.create_signed_url(bucket_name="cover_letters", storage_path=row["storage_path"], expires_in=expires_in)

    def get_cover_letter_file(self, user_id, cover_letter_id):
        if not user_id or not cover_letter_id:
            raise ValueError("User_id and Cover_letter_id are required")

        with connect(self.db_path) as conn:
            row = get_cover_letter(conn, user_id, cover_letter_id)

            if row is None:
                raise ValueError("Cover Letter not found")

        return {
            "cover_letter": self._row_to_cover_letter(row),
            "file_bytes": self.storage_service.download_file(bucket_name="cover_letters", storage_path=row["storage_path"]),
            "content_type": row["content_type"] or "application/octet-stream",
            "original_filename": row["original_filename"] or row["cover_letter_name"] or "cover-letter",
        }
