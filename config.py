import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# ── API Keys ────────────────────────────────────────────────────────────────
# API key is injected via Cloud Run environment variable GOOGLE_API_KEY.
# Do NOT hardcode a key here. The app reads it exclusively from the environment.
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GITHUB_TOKEN   = os.getenv("GITHUB_TOKEN", "")

# ── Highly Available Live Gemini Models ──────────────────────────────────────
# Production-ready models supported by the Google GenAI SDK:
# - MODEL_FLASH: Fast, high-throughput model for document parsing and light agent tasks.
# - MODEL_PRO: Deep reasoning model for 100-pt ATS audits, Google XYZ bullet rewriting,
#   and multi-turn interview evaluation.
MODEL_FLASH = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
MODEL_PRO   = os.getenv("GEMINI_PRO_MODEL", "gemini-2.5-pro")

# ── Resilience Fallback Chain ────────────────────────────────────────────────
# On 503 / 429 / UNAVAILABLE errors the ADKAgent automatically retries
# each live model in this order before raising the final error.
FALLBACK_MODELS = [
    MODEL_FLASH,          # "gemini-2.5-flash" (Primary Flash)
    "gemini-2.0-flash",   # High-speed fallback
    "gemini-1.5-flash",   # Stable tier fallback
    MODEL_PRO,            # "gemini-2.5-pro"   (Deep Reasoning / Last Resort)
]
