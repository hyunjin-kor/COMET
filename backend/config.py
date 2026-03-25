"""Application configuration via environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "CatPrice"
    debug: bool = False

    # Database
    database_url: str = "sqlite:///./catprice.db"

    # Metal price APIs
    metals_dev_api_key: str = ""
    metalprice_api_key: str = ""
    bls_api_key: str = ""

    # Scheduler
    price_update_hour: int = 6  # UTC hour to fetch daily prices

    # Server (used when launched by Electron)
    host: str = "127.0.0.1"
    port: int = 8000

    # CORS — comma-separated list of allowed origins.
    # Defaults cover local dev. For production, set CORS_ORIGINS to your domain.
    # Example: CORS_ORIGINS=https://catprice.example.com,https://www.catprice.example.com
    cors_origins: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS_ORIGINS env var into a list."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
