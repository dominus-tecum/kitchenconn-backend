import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME = "KitchenConn"
    APP_VERSION = "1.0.0"
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./kitchenconn.db")
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")

settings = Settings()