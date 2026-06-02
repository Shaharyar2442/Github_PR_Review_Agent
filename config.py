import os
import warnings
from dotenv import load_dotenv

# Load environment variables from a .env file (if one exists)
load_dotenv()

# Boilerplate configuration loading
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Phase 9: Cloud configuration
DATABASE_URL = os.getenv("DATABASE_URL")
GITHUB_APP_ID = os.getenv("GITHUB_APP_ID")
GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")
GITHUB_PRIVATE_KEY = os.getenv("GITHUB_PRIVATE_KEY")

# Security: Never fall back to a hardcoded secret in production.
# In local dev (no env var set), we generate a random ephemeral secret and warn loudly.
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    JWT_SECRET_KEY = "insecure-local-dev-only-" + os.urandom(16).hex()
    warnings.warn(
        "JWT_SECRET_KEY is not set! Using an insecure random default. "
        "This is acceptable for local development ONLY. "
        "Set JWT_SECRET_KEY in your environment for production.",
        stacklevel=1,
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# CORS: Explicit allow-list. Set ALLOWED_ORIGINS env var as a comma-separated list in production.
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")

if not GITHUB_TOKEN and not GITHUB_APP_ID:
    print("Warning: GITHUB_TOKEN or GITHUB_APP_ID is not set. GitHub API calls will fail.")
if not GROQ_API_KEY:
    print("Warning: GROQ_API_KEY is not set. LLM calls to Groq will fail. Please add it to your .env file.")
