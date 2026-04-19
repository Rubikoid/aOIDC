import datetime
from collections.abc import Mapping, Sequence

from httpx import URL
from joserfc import jwt
from joserfc.errors import BadSignatureError
from pydantic import AnyUrl

from aoidc.errors import (
    GenericOIDCError,
    TokenAudValidationError,
    TokenExpireValidationError,
    TokenFutureValidationError,
    TokenIssuerValidationError,
    TokenValidationError,
)
from aoidc.oauth2.client import BaseOAuth2Client
from aoidc.oauth2.context import ValidationContext
from aoidc.oauth2.rfc_6749_oauth.models import AccessToken
from aoidc.utils import BearerAuth, transform_url, utc_now

from .discovery import MetadataResolver
from .discovery.metadata import Metadata
from .models import GenericIDToken, TokenResponse


class BaseOIDCClient[T: TokenResponse, M: Metadata, MR: MetadataResolver](BaseOAuth2Client[T, M, MR]):
    trusted_auds: Sequence[str] = []

    async def _token_decode(self, token: str | bytes, repeat: int = 0) -> jwt.Token:
        """
        Intellectually decode token even when IDP's JWK keys gets updated.
        """
        if repeat > 1:
            raise TokenValidationError("Invalid signature")

        if not self.keyset:
            raise GenericOIDCError("No keyset")

        try:
            return jwt.decode(
                token,
                self.keyset,
            )
        except BadSignatureError:
            await self.refresh_keyset()
            return await self._token_decode(token, repeat=repeat + 1)

    async def validate_id_token[IDT: GenericIDToken](  # sadly there is no better ways
        self,
        token: str,
        /,
        *,
        token_cls: type[IDT] = GenericIDToken,  # ty:ignore[invalid-parameter-default]
    ) -> IDT:
        # TODO: check for encryption

        # TODO: registry?
        # TODO: alg verification (p7 https://openid.net/specs/openid-connect-core-1_0-final.html#IDTokenValidation)
        raw_token = await self._token_decode(token)

        # run pydantic validators
        parsed_token = token_cls.model_validate(
            raw_token.claims,
            context=ValidationContext(
                origin_url=self.discovery_endpoint,
                allowed_urls=[],  # FIXME: do it.
                settings=self.settings,
            ),
        )
        now = utc_now()

        # check issuer
        if not self.settings.DISABLE_TOKEN_ISSUER_CHECK and parsed_token.iss != self.metadata.issuer:
            raise TokenIssuerValidationError(
                issuer=str(parsed_token.iss),
                metadata_issuer=str(self.metadata.issuer),
            )

        if not self.settings.DISABLE_TOKEN_AUDIENCE_CHECK:
            if not self.CLIENT_ID:
                raise GenericOIDCError("No client_id")

            # check aud
            if isinstance(parsed_token.aud, str):
                if parsed_token.aud != self.CLIENT_ID:
                    raise TokenAudValidationError(parsed_token.aud, (self.CLIENT_ID,))
            else:
                full_trusted_auds = set(self.trusted_auds) | {self.CLIENT_ID}
                auds_diff = parsed_token.aud - full_trusted_auds
                if self.CLIENT_ID not in parsed_token.aud or len(auds_diff) > 0:
                    raise TokenAudValidationError(parsed_token.aud, full_trusted_auds)

        # check DTs
        if not self.settings.DISABLE_TOKEN_EXPIRY_CHECK and parsed_token.exp < now:
            raise TokenExpireValidationError(exp=parsed_token.exp, now=now)

        # WTF: это не против стандарта, но концептуально
        # переделать?
        if not self.settings.DISABLE_TOKEN_EXPIRY_CHECK and (parsed_token.iat - now) > datetime.timedelta(seconds=5):
            raise TokenFutureValidationError(iat=parsed_token.iat, now=now)

        # if isinstance(parsed_token.aud, set):
        #     if not parsed_token.azp:
        #         raise TokenValidationError("`aud` is list, but `azp` does not present")
        # TODO: normal check
        # WTF: https://bitbucket.org/openid/connect/issues/973/
        # WTF: https://stackoverflow.com/questions/41231018/openid-connect-standard-authorized-party-azp-contradiction

        # TODO: check for nonce

        # TODO:
        # if parsed_token.auth_time

        # create claims validator
        # claims_registry = jwt.JWTClaimsRegistry(
        #     iss={"essential": True, "value": str(self.metadata.issuer)},
        #     aud={"essential": True, "values": }
        # )

        # # validate claims
        # claims_registry.validate(parsed_token.model_dump(mode="json"))

        return parsed_token

    async def authorization_code_flow_start(
        self,
        /,
        *,
        redirect_uri: str | AnyUrl | URL | None,
        scopes: Sequence[str] = ("openid",),
        # response_types: Sequence[ResponseType] = (ResponseType.CODE,),
        state: str | None = None,
        # response_mode
        # nonce
        # display
        # prompt
        # max_age
        # ui_locales
        # id_token_hint
        # login_hint
        # acr_values
        extra_data: Mapping[str, str] = {},
    ) -> URL:
        """
        redirect_uri can't be None.
        """

        if "openid" not in scopes:
            raise GenericOIDCError("No `openid` scope defined")

        if redirect_uri is None:
            raise GenericOIDCError("`redirect_uri` can't be None")

        return await super().authorization_code_flow_start(
            redirect_uri=redirect_uri,
            scopes=scopes,
            # response_types=response_types,
            state=state,
            extra_data=extra_data,
        )

    async def authorization_code_flow_continue(
        self,
        /,
        *,
        code: str,
        redirect_uri: str | AnyUrl | URL | None = None,
        state: str | None = None,
        extra_data: Mapping[str, str] = {},
    ) -> T:
        token = await super().authorization_code_flow_continue(
            code=code,
            redirect_uri=redirect_uri,
            state=state,
            extra_data=extra_data,
        )

        return token

    async def authorization_code_flow_finalize[IDT: GenericIDToken](
        self,
        token: T,
        /,
        *,
        token_cls: type[IDT] = GenericIDToken,  # ty:ignore[invalid-parameter-default]
    ) -> IDT:
        id_token = await self.validate_id_token(
            token.id_token,
            token_cls=token_cls,
        )

        return id_token

    async def userinfo(self, token: AccessToken) -> dict:  # TODO: make a model here
        if not self.metadata.userinfo_endpoint:
            raise GenericOIDCError("No `userinfo_endpoint` in metadata")

        response = await self._client.get(
            transform_url(self.metadata.userinfo_endpoint),
            auth=BearerAuth(token),
        )

        return response.json()


class OIDCClient(BaseOIDCClient[TokenResponse, Metadata, MetadataResolver]):
    @classmethod
    def meta_resolver(cls) -> type[MetadataResolver]:
        return MetadataResolver

    @classmethod
    def token_type(cls) -> type[TokenResponse]:
        return TokenResponse
