import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API Keys
    DISCOVERY_API_KEY = os.getenv("DISCOVERY_API_KEY")
    GEMS_API_KEY = os.getenv("GEMS_API_KEY")
    MEDSCHEME_API_KEY = os.getenv("MEDSCHEME_API_KEY")
    
    # Server Config
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./medical_mcp.db")

settings = Settings()