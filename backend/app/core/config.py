"""Application configuration using Pydantic settings."""

from typing import Any

from pydantic import PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "Ring Rookie API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = False
    PUBLIC_URL: str | None = None  # Public URL for webhook callbacks (e.g., ngrok URL)

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "ringrookie"
    DATABASE_URL: PostgresDsn | None = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str | None, info: Any) -> str:
        """Build database URL from components if not provided."""
        if isinstance(v, str):
            return v

        data = info.data
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=data.get("POSTGRES_USER"),
                password=data.get("POSTGRES_PASSWORD"),
                host=data.get("POSTGRES_SERVER"),
                port=data.get("POSTGRES_PORT"),
                path=f"{data.get('POSTGRES_DB') or ''}",
            ),
        )

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None
    REDIS_URL: RedisDsn | None = None

    @field_validator("REDIS_URL", mode="before")
    @classmethod
    def assemble_redis_connection(cls, v: str | None, info: Any) -> str:
        """Build Redis URL from components if not provided."""
        if isinstance(v, str):
            return v

        data = info.data
        password_part = f":{data.get('REDIS_PASSWORD')}@" if data.get("REDIS_PASSWORD") else ""
        return f"redis://{password_part}{data.get('REDIS_HOST')}:{data.get('REDIS_PORT')}/{data.get('REDIS_DB')}"

    # Security
    SECRET_KEY: str = "change-this-to-a-random-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:4170",  # MrAGame
        "http://localhost:4173",  # Ring Rookie frontend
        "http://localhost:8000",
        "https://ring-rookie.vercel.app",
        "https://ringrookie.mragame.com",
        "https://mragame.com",
        "https://www.mragame.com",
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str] | None) -> list[str]:
        """Parse CORS origins from comma-separated string or list."""
        if v is None:
            return []
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Default Admin User (created on first startup if no users exist)
    ADMIN_EMAIL: str = "admin@mragame.com"
    ADMIN_PASSWORD: str = "admin"
    ADMIN_NAME: str = "Admin"

    # Voice & AI Services
    OPENAI_API_KEY: str | None = None
    DEEPGRAM_API_KEY: str | None = None
    ELEVENLABS_API_KEY: str | None = None

    # ChatGPT/Codex OAuth (separate from OpenAI Platform API credentials)
    CHATGPT_OAUTH_ISSUER: str = "https://auth.openai.com"
    CHATGPT_OAUTH_CLIENT_ID: str = "app_EMoamEEZ73f0CkXaXp7hrann"
    CHATGPT_OAUTH_CALLBACK_URL: str = "http://localhost:1455/auth/callback"
    CHATGPT_OAUTH_APP_CALLBACK_URL: str = "http://localhost:8000/api/v1/oauth/chatgpt/callback"
    CHATGPT_OAUTH_RELAY_HOST: str = "127.0.0.1"
    CHATGPT_OAUTH_FRONTEND_URL: str = "http://localhost:4173/dashboard/settings"
    OAUTH_TOKEN_ENCRYPTION_KEY: str | None = None

    # Telephony
    TELNYX_API_KEY: str | None = None
    TELNYX_PUBLIC_KEY: str | None = None
    TWILIO_ACCOUNT_SID: str | None = None
    TWILIO_AUTH_TOKEN: str | None = None

    # External Service Timeouts (seconds)
    # These are critical for preventing hung connections during voice calls
    OPENAI_TIMEOUT: float = 30.0  # LLM inference can be slow
    DEEPGRAM_TIMEOUT: float = 15.0  # Real-time STT should be fast
    ELEVENLABS_TIMEOUT: float = 20.0  # TTS synthesis timeout
    TELNYX_TIMEOUT: float = 10.0  # Telephony API calls
    TWILIO_TIMEOUT: float = 10.0  # Telephony API calls
    GOOGLE_API_TIMEOUT: float = 15.0  # Calendar, Drive, etc.
    DEFAULT_EXTERNAL_TIMEOUT: float = 30.0  # Fallback for other APIs

    # Retry Configuration
    MAX_RETRIES: int = 3  # Number of retry attempts for failed requests
    RETRY_BACKOFF_FACTOR: float = 2.0  # Exponential backoff multiplier

    # Monitoring
    SENTRY_DSN: str | None = None
    SENTRY_ENVIRONMENT: str = "development"
    SENTRY_TRACES_SAMPLE_RATE: float = 1.0

    # OpenTelemetry
    OTEL_ENABLED: bool = False
    OTEL_SERVICE_NAME: str = "ringrookie-api"
    OTEL_EXPORTER_OTLP_ENDPOINT: str | None = None


settings = Settings()
