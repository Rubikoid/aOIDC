import warnings
from typing import Self

from pydantic import BaseModel, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ProcessingSettings(BaseModel):
    """
    These settings are the most secure and sane defaults, that I can imagine.

    But they are also highly configurable, so if needed - any part can be easy tweaked.
    """

    ALLOW_HTTP: bool = False
    """
        This option violates the RFCs, but may be useful for debugging, and MUST NOT be enabled in production env

        Allows making request by HTTP.
    """

    ALLOW_ALG_NONE: bool = False
    """
        This option violates the RFCs, but may be useful for debugging, and MUST NOT be enabled in production env

        Allows fetching metadata with `none` in `alg`.

        Allows validating tokens with `alg` = `none`.
    """

    ALLOW_ALL_URLS: bool = False
    """
        This option is INSECURE, but may be useful for debugging, and MUST NOT be enabled in production env

        Disables any same origin URL checks.
    """

    DEFAULT_CLIENT_NO_VERIFY: bool = False
    """
        This option is INSECURE, but may be useful for debugging, and MUST NOT be enabled in production env

        Disables SSL verify in default client.
    """

    FOLLOW_REDIRECTS: bool = False
    """
        This option is OPTIONATED

        This option WILL APPLY to any HTTP client, passed to BaseOAuth2Client, since it have implict on security
    """

    DISALBE_TOKEN_ISSUER_CHECK: bool = False
    """
        This option is INSECURE, but may be useful for debugging, and MUST NOT be enabled in production env

        This option will disable token issuer check
    """

    DISALBE_TOKEN_AUDIENCE_CHECK: bool = False
    """
        This option is INSECURE, but may be useful for debugging, and MUST NOT be enabled in production env

        This option will disable token audience check
    """

    DISALBE_TOKEN_EXPIRY_CHECK: bool = False
    """
        This option is INSECURE, but may be useful for debugging, and MUST NOT be enabled in production env

        This option will disable token expiry check
    """

    def _clone_with(self, **kwargs: dict[str, bool]) -> Self:
        return self.model_copy(update=kwargs)

    @classmethod
    def global_clone_with(cls, **kwargs: dict[str, bool]) -> Self:
        # WTF(rubikoid): shitfix. Think about it to make this better
        return cls.model_validate(settings.model_dump())._clone_with(**kwargs)  # noqa: SLF001


class _Settings(ProcessingSettings, BaseSettings):
    DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_prefix="AOIDC_",
    )

    @model_validator(mode="after")
    def warn_usage_of_debug_options(self) -> Self:
        if self.ALLOW_HTTP:
            warnings.warn("Globally enabled RFC violation option ALLOW_HTTP", stacklevel=1)

        if self.ALLOW_ALG_NONE:
            warnings.warn("Globally enabled RFC violation option ALLOW_ALG_NONE", stacklevel=1)

        if self.ALLOW_ALL_URLS:
            warnings.warn("Globally enabled potential insecure option ALLOW_ALL_URLS", stacklevel=1)

        if self.DEFAULT_CLIENT_NO_VERIFY:
            warnings.warn("Globally enabled potential insecure option DEFAULT_CLIENT_NO_VERIFY", stacklevel=1)

        if self.DISALBE_TOKEN_ISSUER_CHECK:
            warnings.warn("Globally enabled insecure option DISALBE_TOKEN_ISSUER_CHECK", stacklevel=1)

        if self.DISALBE_TOKEN_AUDIENCE_CHECK:
            warnings.warn("Globally enabled insecure option DISALBE_TOKEN_AUDIENCE_CHECK", stacklevel=1)

        if self.DISALBE_TOKEN_EXPIRY_CHECK:
            warnings.warn("Globally enabled insecure option DISALBE_TOKEN_EXPIRY_CHECK", stacklevel=1)

        return self


settings = _Settings()
