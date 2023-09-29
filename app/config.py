from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_hostname: str
    db_port: int
    db_username: str
    db_password: str
    model_config = SettingsConfigDict(env_file=".env")


config = Settings()
