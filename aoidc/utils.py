from collections.abc import Generator
import datetime
from typing import Annotated

from httpx import URL, Auth, Request, Response
from pydantic import AnyUrl, AwareDatetime

UTCTime = Annotated[AwareDatetime, ...]


def is_same_origin(url_1: str | AnyUrl | URL, url_2: str | AnyUrl | URL) -> bool:
    """
    Checks if two urls has the same origin - same (scheme, host, port)
    """

    url_1 = transform_url(url_1)
    url_2 = transform_url(url_2)

    _t1 = (url_1.scheme, url_1.host, url_1.port)
    _t2 = (url_2.scheme, url_2.host, url_2.port)

    if _t1 != _t2:
        return False
    return True


def transform_url(url: str | AnyUrl | URL) -> URL:
    if isinstance(url, AnyUrl):
        return URL(url.unicode_string())
    return URL(url)


def utc_now() -> UTCTime:
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


# def patch_url(
#     url: AnyUrl,
#     /,
#     *,
#     scheme: str | None = None,
#     username: str | None = None,
#     password: str | None = None,
#     host: str | None = None,
#     port: int | None = None,
#     path: str | None = None,
#     query: str | None = None,
#     fragment: str | None = None,
# ) -> AnyUrl:
#     scheme = url.scheme if scheme is None else scheme
#     username = url.username if username is None else username
#     password = url.password if password is None else password
#     host = url.host if host is None else host
#     port = url.port if port is None else port
#     path = url.path if path is None else path
#     query = url.query if query is None else query
#     fragment = url.fragment if fragment is None else fragment

#     if host is None:
#         raise ValueError("Host is None")

#     return url.build(
#         scheme=scheme,
#         username=username,
#         password=password,
#         host=host,
#         port=port,
#         path=path,
#         query=query,
#         fragment=fragment,
#     )
