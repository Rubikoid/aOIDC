import datetime
from collections.abc import Generator
from typing import Annotated

from httpx import URL, Auth, Request, Response
from pydantic import AnyUrl, AwareDatetime

UTCTime = Annotated[AwareDatetime, ...]


def is_same_origin(url_1: str | AnyUrl | URL, url_2: str | AnyUrl | URL) -> bool:
    """
    Check if two urls has the same origin - same (scheme, host, port).
    """

    url_1 = transform_url(url_1)
    url_2 = transform_url(url_2)

    _t1 = (url_1.scheme, url_1.host, url_1.port)
    _t2 = (url_2.scheme, url_2.host, url_2.port)

    if _t1 != _t2:  # noqa: SIM103
        return False
    return True


def transform_url(url: str | AnyUrl | URL) -> URL:
    """
    Transform any url - str, pydantic.AnyUrl or httpx.URL to httpx.URL.
    """

    if isinstance(url, AnyUrl):
        return URL(url.unicode_string())
    return URL(url)


def utc_now() -> UTCTime:
    """
    Generate utc timezone-aware datetime.
    """

    return datetime.datetime.now(datetime.UTC)


class BearerAuth(Auth):
    """
    ...
    """

    def __init__(self, token: str) -> None:
        self._auth_header = self._build_auth_header(token)

    def auth_flow(self, request: Request) -> Generator[Request, Response, None]:
        request.headers["Authorization"] = self._auth_header
        yield request

    def _build_auth_header(self, token) -> str:
        return f"Bearer {token}"
