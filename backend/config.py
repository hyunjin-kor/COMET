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

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
