"""Configurações da aplicação via variáveis de ambiente."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações carregadas de variáveis de ambiente."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Servidor
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # Banco de dados
    database_url: str = "sqlite:///./transacoes.db"


settings = Settings()