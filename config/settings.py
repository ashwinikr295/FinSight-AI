import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_PDF_DIR = DATA_DIR / "raw_pdfs"
MARKDOWN_DIR = DATA_DIR / "markdown"
DB_PATH = DATA_DIR / "investor_intelligence.db"

RAW_PDF_DIR.mkdir(parents=True, exist_ok=True)
MARKDOWN_DIR.mkdir(parents=True, exist_ok=True)

# Azure / OpenAI / Gemini Configuration (Optional)
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY", "")
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Database Config
POSTGRES_DB_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

# App Settings
USE_LOCAL_FALLBACK = True if not (AZURE_OPENAI_API_KEY or OPENAI_API_KEY or GEMINI_API_KEY) else False
