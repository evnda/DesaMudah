import os
from dotenv import load_dotenv

# Membaca konfigurasi dari file .env
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")

    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "desa_mudah")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
