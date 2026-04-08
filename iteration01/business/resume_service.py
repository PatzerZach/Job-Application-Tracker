import os
import uuid

from dal.db import connect
from dal.resumes_q import create_resume, delete_resume, get_resume, list_resumes_by_user
from business.resume import Resume

class ResumeService:
    def __init__(self, db_path, storage_service):
        self.db_path = db_path
        self.storage_service = storage_service
        
    def _row_to_resume(self, row):
        return Resume(
            resume_id=row["id"],
            user_id=row["user_fk"],
            resume_name=row["resume_name"],
            storage_path=row["storage_path"],
            original_filename=row["original_filename"],
            content_type=row["content_type"]
        )
        
    def create_resume(self, user_id, resume_name, file_bytes, original_filename, content_type):
        if not user_id:
            raise ValueError("User ID is required")
        
        if not resume_name or not resume_name.strip():
            raise ValueError("Resume name is required")
        
        if not file_bytes:
            raise ValueError("Uploaded file is required")
        
        if not original_filename:
            raise ValueError("Original filename is required")
        
        allowed_types = {
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }
        
        if content_type not in allowed_types:
            raise ValueError("Invalid file type. Only PDF, DOC, and DOCX are allowed")
        
        safe_resume_name = resume_name.strip()
        extension = os.path.splitext(original_filename)[1].lower()
        unique_name = f"{uuid.uuid4()}{extension}"
        storage_path = f"{user_id}/{unique_name}"
        
        stored_path = self.storage_service.upload_file(bucket_name="resumes", storage_path=storage_path, file_bytes=file_bytes, content_type=content_type)
        
        with connect(self.db_path) as conn:
            resume_id = create_resume(
                conn=conn, 
                user_id=user_id,
                resume_name=safe_resume_name,
                storage_path=stored_path,
                original_filename=original_filename,
                content_type=content_type
            )
            
        return resume_id
    
    def get_resume(self, user_id, resume_id):
        if not user_id or not resume_id:
            raise ValueError("User_id and resume_id are required")
        
        with connect(self.db_path) as conn:
            row = get_resume(conn, user_id, resume_id)
            
        if row is None:
            return None
        
        return self._row_to_resume(row)
    
    def list_resumes(self, user_id, limit=50, offset=0, sort="id", direction="DESC"):
        if not user_id:
            raise ValueError("User_id is required")
        
        with connect(self.db_path) as conn:
            rows = list_resumes_by_user(conn, user_id, limit, offset, sort, direction)
            
        return [self._row_to_resume(row) for row in rows]
    
    def delete_resume(self, user_id, resume_id):
        if not user_id or not resume_id:
            raise ValueError("User_id and Resume_id are required")
        
        with connect(self.db_path) as conn:
            row = get_resume(conn, user_id, resume_id)
            
            if row is None:
                raise ValueError("Resume not found")
            
            storage_path = row["storage_path"]
            
            self.storage_service.delete_file(bucket_name="resumes", storage_path=storage_path)
            
            delete_resume(conn, user_id, resume_id)
            
        return True
    
    def get_resume_download_url(self, user_id, resume_id, expires_in=3600):
        if not user_id or not resume_id:
            raise ValueError("User_id and Resume_id are required")
        
        with connect(self.db_path) as conn:
            row = get_resume(conn, user_id, resume_id)
            
            if row is None:
                raise ValueError("Resume not found")
            
            return self.storage_service.create_signed_url(bucket_name="resumes", storage_path=row["storage_path"], expires_in=expires_in)
