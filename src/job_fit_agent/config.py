"""Application settings loaded from environment variables."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # France Travail API (https://francetravail.io)
    ft_client_id: str = ""
    ft_client_secret: str = ""
    ft_scope: str = "api_offresdemploiv2 o2dsoffre"
    ft_token_url: str = (
        "https://entreprise.francetravail.fr/connexion/oauth2/"
        "access_token?realm=/partenaire"
    )
    ft_api_base: str = "https://api.francetravail.io/partenaire"


settings = Settings()


class LLMSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    # Swap this freely — e.g. anthropic/claude-sonnet-4.5, openai/gpt-4o, etc.
    llm_model: str = "anthropic/claude-sonnet-4.5"


llm_settings = LLMSettings()
