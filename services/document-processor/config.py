import os
from pathlib import Path
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.supabase_jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
        
        # Configuration pour le traitement des documents
        self.temp_dir = Path("temp")
        self.max_file_size = int(os.getenv("MAX_FILE_SIZE_MB", 10)) * 1024 * 1024  # 10 MB par défaut
        
        # Création du dossier temporaire
        self.temp_dir.mkdir(parents=True, exist_ok=True)