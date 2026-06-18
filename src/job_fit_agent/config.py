"""Application settings loaded from environment variables."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # France Travail API credentials (https://francetravail.io)
    ft_client_id: str = ""
    ft_client_secret: str = ""
    ft_token_url: str = (
        "https://entreprise.francetravail.fr/connexion/oauth2/access_token"
    )
    ft_api_base: str = "https://api.francetravail.io/partenaire"


settings = Settings()
