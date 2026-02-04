"""
Implementation of https://datatracker.ietf.org/doc/html/rfc8414#section-3
"""

from pathlib import PurePosixPath
from typing import Sequence

from httpx import URL, AsyncClient

from aoidc.oauth2.context import ValidationContext

from .metadata import Metadata


class BaseMetadataResolver[M: Metadata]:
    _well_known = ".well-known/oauth-authorization-server"

    @classmethod
    def _metadata_cls(cls) -> type[M]:
        raise NotImplementedError

    @classmethod
    def _transform_url(cls, url: URL) -> URL:
        """
        Normalize url to _well_known path

        If `url` already contains `.well-known/oauth-authorization-server` don't do anything to url

        If `url` does not contains path - sets path to `.well-known/oauth-authorization-server`

        If `url` contains any other path - formats as `.well-known/oauth-authorization-server/{path}`
        """

        if not url.path or cls._well_known not in url.path:
            url = url.copy_with(
                path=str(PurePosixPath(cls._well_known) / url.path),  # PurePosixPath is a creative solution...
            )

        return url

    @classmethod
    async def resolve_metadata(
        cls,
        client: AsyncClient,
        url: URL,
        whitelisted_urls: Sequence[URL] = [],
    ) -> M:
        """
        Resolve oauth metadata from remote server using `client`

        Uses url tranformation via `_transform_url`

        `whitelisted_urls` is required to validate urls, parsed in Metadata
        """

        url = cls._transform_url(url)
        response = await client.get(url)
        response.raise_for_status()

        parsed_metadata = cls._metadata_cls().model_validate_json(
            response.text,
            context=ValidationContext(
                origin_url=url,
                allowed_urls=whitelisted_urls,
            ),
        )

        return parsed_metadata


class MetadataResolver(BaseMetadataResolver[Metadata]):
    @classmethod
    def _metadata_cls(cls) -> type[Metadata]:
        return Metadata
