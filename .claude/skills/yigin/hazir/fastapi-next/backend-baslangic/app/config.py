"""Uygulama ayarları.

Değerler ortam değişkenlerinden okunur. Gizli değerler (parola, SECRET_KEY) kök .env
dosyasından, gizli olmayan bağlantı bilgileri (DB_HOST, REDIS_HOST, SMTP_HOST)
compose dosyasındaki x-python-env bloğundan gelir.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    app_name: str = "app"
    app_env: str = "local"
    secret_key: str = ""

    db_host: str = "db"
    db_port: int = 5432
    db_database: str = ""
    db_username: str = ""
    db_password: str = ""

    redis_host: str = "redis"
    redis_port: int = 6379

    # Mailpit eki seçildiyse yerelde "mailpit"; seçilmediyse boş kalır.
    smtp_host: str = ""
    smtp_port: int = 1025

    @property
    def database_url(self) -> URL:
        # URL.create parolayı güvenle kaçışlar; parolada @ veya : olsa da bağlantı bozulmaz.
        return URL.create(
            "postgresql+asyncpg",
            username=self.db_username,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            database=self.db_database,
        )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/0"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
