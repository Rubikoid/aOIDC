from pydantic import AnyUrl


def is_same_origin(url1: AnyUrl, url2: AnyUrl) -> bool:
    """
    Checks if two urls has the same origin - same (scheme, host, port)
    """
    if (url1.scheme, url1.host, url1.port) != (url2.scheme, url2.host, url2.port):
        return False
    return True
