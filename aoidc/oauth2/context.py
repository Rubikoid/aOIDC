"""
Helper module for passing validation context.
"""

from collections.abc import Sequence
from dataclasses import dataclass, field

from httpx import URL

from aoidc.config import ProcessingSettings


@dataclass(init=True, frozen=True, slots=True)
class ValidationContext:
    origin_url: URL

    settings: ProcessingSettings

    allowed_urls: Sequence[URL] = field(default_factory=list)
