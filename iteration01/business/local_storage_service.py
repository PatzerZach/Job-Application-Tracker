from pathlib import Path

class LocalStorageService:
    def __init__(self, base_dir="uploads"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def upload_file(self, bucket_name, storage_path, file_bytes, content_type):
        file_path = self.base_dir / bucket_name / storage_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(file_bytes)
        return storage_path

    def delete_file(self, bucket_name, storage_path):
        file_path = self.base_dir / bucket_name / storage_path
        if file_path.exists():
            file_path.unlink()
        return True

    def create_signed_url(self, bucket_name, storage_path, expires_in=3600):
        return f"/local-file/{bucket_name}/{storage_path}"

    def download_file(self, bucket_name, storage_path):
        file_path = self.base_dir / bucket_name / storage_path
        if not file_path.exists():
            raise ValueError("Stored file was not found")
        return file_path.read_bytes()
