from dal.db import connect

class StorageService:
    def __init__(self, db_path):
        self.db_path = db_path
        
    