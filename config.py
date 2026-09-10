import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# ── API Keys ────────────────────────────────────────────────────────────────
# API key is injected via Cloud Run environment variable GOOGLE_API_KEY.
# Do NOT hardcode a key here. The app reads it exclusively from the environment.
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GITHUB_TOKEN   = os.getenv("GITHUB_TOKEN", "")

# ── Model Configuration ──────────────────────────────────────────────────────
# Primary model: Gemini 3.8 Flash (latest available flash model as of Sep 2026).
# Released: Sep 2, 2026. Features: 1M-token context, 64K output, optimized for
# autonomous agents and complex reasoning.
# Override via GEMINI_MODEL env var if needed.
MODEL_FLASH = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
MODEL_PRO   = os.getenv("GEMINI_PRO_MODEL", "gemini-2.5-pro")

# ── Resilience Fallback Chain ────────────────────────────────────────────────
# On 503 / 429 / UNAVAILABLE errors the ADKAgent automatically retries
# each model in this order before raising the final error.
#
#  Phase 1  →  gemini-3.8-flash       (primary — latest & most capable flash)
#  Phase 2  →  gemini-3.7-flash       (first fallback — Aug 2026)
#  Phase 3  →  gemini-3.6-flash       (second fallback — Jul 2026)
#  Phase 4  →  gemini-2.5-flash       (third fallback — stable tier)
#  Phase 5  →  gemini-2.0-flash       (fourth fallback — widely available)
#  Phase 6  →  gemini-2.5-pro         (last resort — most capable but slower)
#
FALLBACK_MODELS = [
    "gemini-3.8-flash",   # Phase 1 — primary (latest)
    "gemini-3.7-flash",   # Phase 2
    "gemini-3.6-flash",   # Phase 3
    "gemini-2.5-flash",   # Phase 4
    "gemini-2.0-flash",   # Phase 5
    MODEL_PRO,            # Phase 6 — last resort
]
