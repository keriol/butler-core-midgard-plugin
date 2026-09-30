from __future__ import annotations

from typing import Protocol

from .contracts import MidgardRequest, MidgardResult
from .observability import RoutingEvent


class CoreRequestHandler(Protocol):
    async def handle(self, request: MidgardRequest) -> MidgardResult:
        """Handle one Midgard request on the Butler Core-facing side."""
        ...


class AsgardTarget(Protocol):
    """Butler-owned ingress visible to Midgard through a neutral port."""

    @property
    def available(self) -> bool:
        """Return whether the Butler-owned ingress is currently addressable."""
        ...

    def matches_butler_name(self, requested_name: str) -> bool:
        """Answer whether this Asgard belongs to the requested Butler."""
        ...

    @property
    def butler_name(self) -> str:
        """Return this Asgard's authoritative Butler identity."""
        ...

    async def handle(self, request: MidgardRequest) -> MidgardResult:
        """Forward the request into this Asgard's Butler."""
        ...


class MidgardObserver(Protocol):
    """Neutral observability sink.

    A concrete Butler host may adapt this port to its own observability system.
    """

    def record(self, event: RoutingEvent) -> None:
        ...
