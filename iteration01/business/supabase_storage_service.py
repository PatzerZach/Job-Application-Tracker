from supabase import create_client

class SupbaseStorageService:
    def __init__(self, supabase_url, supabase_key):
        if not supabase_url or not supabase_key:
            raise ValueError("Supabase URL and key are required")

        self.client = create_client(supabase_url, supabase_key)

    def upload_file(self, bucket_name, storage_path, file_bytes, content_type):
        response = self.client.storage.from_(bucket_name).upload(
            storage_path,
            file_bytes,
            {"content-type": content_type}
        )
        return storage_path
    
    def delete_file(self, bucket_name, storage_path):
        self.client.storage.from_(bucket_name).remove([storage_path])
        return True

    def create_signed_url(self, bucket_name, storage_path, expires_in=3600):
        response = self.client.storage.from_(bucket_name).create_signed_url(
            storage_path,
            expires_in
        )

        if isinstance(response, dict):
            return response.get("signedURL") or response.get("signed_url")

        if hasattr(response, "get"):
            return response.get("signedURL") or response.get("signed_url")

        raise ValueError("Could not create signed URL")
