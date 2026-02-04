"""
Implementation of https://openid.net/specs/openid-connect-discovery-1_0-final.html.
"""

from pathlib import PurePosixPath

from httpx import URL

from aoidc.oauth2.rfc_8414_server_metadata.resolver import BaseMetadataResolver

from .metadata import Metadata


class MetadataResolver(BaseMetadataResolver[Metadata]):
    @classmethod
    def _metadata_cls(cls) -> type[Metadata]:
        return Metadata

    _well_known = ".well-known/openid-configuration"

    @classmethod
    def _transform_url(cls, url: URL) -> URL:
        """
        Normalize url to _well_known path.

        If `url` already contains `.well-known/openid-configuration` don't do anything to url

        If `url` does not contains path - sets path to `.well-known/openid-configuration`

        If `url` contains any other path - formats as `/{path}/.well-known/openid-configuration`

        ref: https://datatracker.ietf.org/doc/html/rfc8414#section-5
        ref: https://openid.net/specs/openid-connect-discovery-1_0-final.html#ProviderConfigurationRequest
        """

        if not url.path or cls._well_known not in url.path:
            url = url.copy_with(
                path=str(
                    PurePosixPath(url.path) / PurePosixPath(cls._well_known),
                ),  # PurePosixPath is a creative solution...
            )

        return url
