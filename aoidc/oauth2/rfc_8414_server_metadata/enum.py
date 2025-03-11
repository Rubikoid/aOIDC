# ruff: noqa: S105
from enum import StrEnum


class ResponseModes(StrEnum):
    query = "query"
    fragment = "fragment"
    form_post = "form_post"
