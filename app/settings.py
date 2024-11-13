from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    postgres_db_name: str
    postgres_db_user: str
    postgres_db_password: str
    postgres_db_host: str
    postgres_db_port: int
    postgres_db_dsn: str = (
        f"postgresql://{postgres_db_name}:{postgres_db_password}@{postgres_db_host}:{postgres_db_port}/{postgres_db_name}"
    )

    rabbitmq_queue_name: str
    rabbitmq_host: str
    rabbitmq_port: int
    rabbitmq_user: str
    rabbitmq_password: str


settings = Settings(_env_file=".env", _env_file_encoding="utf-8")
