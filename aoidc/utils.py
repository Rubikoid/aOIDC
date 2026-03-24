import datetime
import warnings
from collections.abc import Generator
from typing import Annotated, Any

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


def show_unknown_enum_waring(enum_name: str, unknown_value: Any) -> None:  # noqa: ANN401
    warnings.warn(
        "A new, unknown enum value was detected. "
        f"Enum: {enum_name!r}, value: {unknown_value!r}. "
        "Please create an issue at https://github.com/Rubikoid/aOIDC/issues/new "
        "with a copy of this error and the name or address of the OIDC provider "
        "you are using so I can add this value to the enum.",
        stacklevel=2,
    )


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
