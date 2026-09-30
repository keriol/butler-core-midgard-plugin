from __future__ import annotations

from typing import Protocol

from .contracts import MidgardRequest, MidgardResult


class CoreRequestHandler(Protocol):
    async def handle(self, request: MidgardRequest) -> MidgardResult:
        """Handle one Midgard request on the Butler Core-facing side."""
        ...
