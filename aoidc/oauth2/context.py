"""
Helper module for passing validation context
"""

from dataclasses import dataclass, field

from pydantic import AnyUrl


@dataclass(init=True, frozen=True, slots=True)
class ValidationContext:
    origin_url: AnyUrl

    allowed_urls: list[AnyUrl] = field(default_factory=list)
