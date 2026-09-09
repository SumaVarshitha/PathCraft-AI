import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

# Highly available Gemini models with automatic resilience fallback
MODEL_FLASH = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
MODEL_PRO = os.getenv("GEMINI_PRO_MODEL", "gemini-2.5-pro")

FALLBACK_MODELS = [
    MODEL_FLASH,
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-2.5-pro"
]
