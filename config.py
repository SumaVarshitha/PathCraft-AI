import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

# Default Gemini Models
MODEL_FLASH = "gemini-3.6-flash"
MODEL_PRO = "gemini-3.6-pro"
