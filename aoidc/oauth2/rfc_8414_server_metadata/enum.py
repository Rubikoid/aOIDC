from enum import StrEnum

from aoidc.utils import show_unknown_enum_waring


class ResponseModes(StrEnum):
    QUERY = "query"
    FRAGMENT = "fragment"
    FORM_POST = "form_post"

    # keycloak, idk
    JWT = "jwt"
    QUERY_JWT = "query.jwt"
    FRAGMENT_JWT = "fragment.jwt"
    FORM_POST_JWT = "form_post.jwt"

    _UNKNOWN = "_UNKNOWN"

    @classmethod
    def _missing_(cls, value):
        show_unknown_enum_waring(cls.__name__, value)
        return cls._UNKNOWN
