import os

class APIConfig:
    HOST: str = os.environ.get("API_HOST", "0.0.0.0")
    PORT: int = int(os.environ.get("API_PORT", 8000))
    RELOAD: bool = os.environ.get("API_RELOAD", "true").lower() in ("true", "1", "t")
    WORKERS: int = int(os.environ.get("API_WORKERS", 1))
    CORS_ORIGINS: list[str] = [origin.strip() for origin in os.environ.get("API_CORS_ORIGINS", "*").split(",")]
    API_TITLE: str = "JATS Import/Export API"
    API_DESCRIPTION: str = "An API for uploading JATS documents, importing them to different storage backends (e.g. Plone), and converting them to various formats."
    API_VERSION: str = "1.0.0"

class StorageConfig:
    STORAGE_ADAPTER: str = os.environ.get("STORAGE_ADAPTER", "plone")
    CONTAINER: str | None = os.environ.get("STORAGE_CONTAINER", None)
