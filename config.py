import os
from dotenv import load_dotenv

# Load environment variables from a .env file (if one exists)
load_dotenv()

# Boilerplate configuration loading
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Phase 9: Cloud configuration
DATABASE_URL = os.getenv("DATABASE_URL")
GITHUB_APP_ID = os.getenv("GITHUB_APP_ID")
GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")
GITHUB_PRIVATE_KEY = os.getenv("GITHUB_PRIVATE_KEY")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-key-for-local-dev-change-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days

if not GITHUB_TOKEN and not GITHUB_APP_ID:
    print("Warning: GITHUB_TOKEN or GITHUB_APP_ID is not set. GitHub API calls will fail.")
if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY is not set. LLM calls to Gemini will fail. Please add it to your .env file.")
