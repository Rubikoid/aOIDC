"""
Implements https://openid.net/specs/openid-connect-discovery-1_0-final.html
"""

from httpx import URL, AsyncClient

from aoidc.oauth2.context import ValidationContext

from .metadata import Metadata


async def resolve_metadata(client: AsyncClient, url: URL) -> Metadata:
    _well_known = ".well-known/openid-configuration"

    # В https://datatracker.ietf.org/doc/html/rfc8414#section-3.1 пишут, что имеющийся путь надо приколачивать
    # ПОСЛЕ `.well-known/openid-configuration`
    # В https://openid.net/specs/openid-connect-discovery-1_0-final.html#ProviderConfigurationRequest пишут, что
    # имеющийся путь надо приколачивать ДО `.well-known/openid-configuration`
    # я лично рот шатал авторов этих стандартов, которые сам себе противоречат, поэтому принимаем соломоново решениие и
    # 1) просто полностью игнорируем исходный путь, если в нём нет well-known заклинания
    # 2) если же оно есть - считаем, что пользователь библиотеки умный и знает, куда надо ходить за конфигом
    # TODO: https://datatracker.ietf.org/doc/html/rfc8414#section-5

    if not url.path or _well_known not in url.path:
        url = url.copy_with(path=_well_known)

    response = await client.get(url)

    parsed_metadata = Metadata.model_validate_json(
        response.text,
        context=ValidationContext(
            origin_url=url,
            allowed_urls=[],  # TODO: pass value here
        ),
    )

    return parsed_metadata
