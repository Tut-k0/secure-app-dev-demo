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
    azure_blob_connection_string: str
    azure_blob_storage_name: str
    azure_blob_container_name: str
    azure_blob_sas_token: str
    model_config = SettingsConfigDict(env_file=".env")


config = Settings()
