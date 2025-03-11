from pydantic_settings import BaseSettings, SettingsConfigDict


class _Settings(BaseSettings):
    DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_prefix="AOIDC_",
    )


settings = _Settings()
