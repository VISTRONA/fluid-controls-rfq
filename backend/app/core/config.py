from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Fluid Controls RFQ API"
    app_version: str = "0.1.0"

    database_url: str = (
        "mysql+pymysql://rfq_user:rfq_dev_password@db:3306/fluid_controls_rfq"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
