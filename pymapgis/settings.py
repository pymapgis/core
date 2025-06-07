from pydantic_settings import BaseSettings, SettingsConfigDict


class _Settings(BaseSettings):
    cache_dir: str = "~/.cache/pymapgis"
    default_crs: str = "EPSG:4326"

    model_config = SettingsConfigDict(env_prefix="PYMAPGIS_", extra="ignore")


settings = _Settings()
