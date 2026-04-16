import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Database — auto-detects SQLite for local dev, PostgreSQL in Docker
    _db_url = os.getenv("DATABASE_URL", "")
    DATABASE_URL: str = _db_url if _db_url else "sqlite:///./booksmart.db"

    # Exotel API (replacing Twilio)
    EXOTEL_ACCOUNT_SID: str = os.getenv("EXOTEL_ACCOUNT_SID", "mock_exotel_sid")
    EXOTEL_API_KEY: str = os.getenv("EXOTEL_API_KEY", "mock_api_key")
    EXOTEL_API_TOKEN: str = os.getenv("EXOTEL_API_TOKEN", "mock_api_token")
    EXOTEL_APP_ID: str = os.getenv("EXOTEL_APP_ID", "mock_app_id")
    EXOTEL_PHONE_NUMBER: str = os.getenv("EXOTEL_PHONE_NUMBER", "+91YOUR_CUSTOM_NUMBER")

    # AI Keys
    GEMINI_API_KEY: str  = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY: str    = os.getenv("GROQ_API_KEY",   "")

    # Voice APIs (STT/TTS using Google & Deepgram)
    GOOGLE_TTS_API_KEY: str = os.getenv("GOOGLE_TTS_API_KEY", "")
    DEEPGRAM_API_KEY: str = os.getenv("DEEPGRAM_API_KEY", "")

    # JWT Authentication
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "booksmart-ai-super-secret-key-change-in-production")

    # Razorpay Payments
    RAZORPAY_KEY_ID: str     = os.getenv("RAZORPAY_KEY_ID",     "")
    RAZORPAY_KEY_SECRET: str = os.getenv("RAZORPAY_KEY_SECRET", "")

    # Email / SMTP (Gmail)
    SMTP_EMAIL: str    = os.getenv("SMTP_EMAIL",    "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")


settings = Settings()
