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

    # Local loopback sidecar used by Electron
    host: str = "127.0.0.1"
    port: int = 8000

    # Loopback-only origins used by Vite during local desktop development.
    cors_origins: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"
    allowed_hosts: str = "127.0.0.1,localhost,testserver"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS_ORIGINS env var into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def allowed_hosts_list(self) -> list[str]:
        """Parse ALLOWED_HOSTS env var into a list."""
        return [host.strip() for host in self.allowed_hosts.split(",") if host.strip()]


settings = Settings()
