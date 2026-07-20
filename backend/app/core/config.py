import os


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        user = os.getenv("POSTGRES_USER", "postgres")
        password = os.getenv("POSTGRES_PASSWORD", "postgres")
        # default to postgres service in docker
        host = os.getenv("POSTGRES_HOST", "postgres")
        db = os.getenv("POSTGRES_DB", "library_db")
        DATABASE_URL = f"postgresql://{user}:{password}@{host}:5432/{db}"

    CELERY_BROKER_URL: str = os.getenv(
        "CELERY_BROKER_URL", "redis://redis:6379/0"
    )
    CELERY_RESULT_BACKEND: str = os.getenv(
        "CELERY_RESULT_BACKEND", "redis://redis:6379/0"
    )

    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY",
        "super-secret-library-key-change-me-in-production"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60


settings = Settings()
