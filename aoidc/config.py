from pydantic_settings import BaseSettings, SettingsConfigDict


class _Settings(BaseSettings):
    DEBUG: bool = False

    ALLOW_HTTP: bool = False
    """This option violates the RFCs, but may be useful for debugging, and MUST NOT be enabled in production env"""

    ALLOW_ALG_NONE: bool = False
    """This option violates the RFCs, but may be useful for debugging, and MUST NOT be enabled in production env"""

    ALLOW_ALL_URLS: bool = False
    """This option is INSECURE, but may be useful for debugging, and MUST NOT be enabled in production env"""

    model_config = SettingsConfigDict(
        env_prefix="AOIDC_",
    )


settings = _Settings()
