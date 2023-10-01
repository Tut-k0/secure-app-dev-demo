from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_hostname: str
    db_port: int
    db_name: str
    db_username: str
    db_password: str
    secret_key: str
    algorithm: str
    token_expire_minutes: int
    model_config = SettingsConfigDict(env_file=".env")


config = Settings()
