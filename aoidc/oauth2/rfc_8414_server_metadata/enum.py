from enum import StrEnum


class ResponseModes(StrEnum):
    QUERY = "query"
    FRAGMENT = "fragment"
    FORM_POST = "form_post"

    # keycloak, idk
    JWT = "jwt"
    QUERY_JWT = "query.jwt"
    FRAGMENT_JWT = "fragment.jwt"
    FORM_POST_JWT = "form_post.jwt"
