# ruff: noqa: S105
from enum import StrEnum


class ResponseModes(StrEnum):
    QUERY = "query"
    FRAGMENT = "fragment"
    FORM_POST = "form_post"

