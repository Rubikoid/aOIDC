"""
Helper module for passing validation context
"""

from dataclasses import dataclass, field

from httpx import URL


@dataclass(init=True, frozen=True, slots=True)
class ValidationContext:
    origin_url: URL

    allowed_urls: list[URL] = field(default_factory=list)
