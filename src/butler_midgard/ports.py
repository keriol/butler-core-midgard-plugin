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
    def butler_name(self) -> str:
        """Return the authoritative Butler identity owned by this Asgard."""
        ...

    @property
    def available(self) -> bool:
        """Return whether the Butler-owned ingress is currently addressable."""
        ...

    async def handle(self, request: MidgardRequest) -> MidgardResult:
        """Forward the request into this Asgard's Butler."""
        ...


class MidgardObserver(Protocol):
    """Neutral observability sink.

    Alfred may adapt this port to Georges without making Midgard depend on
    Alfred or on any concrete observability implementation.
    """

    def record(self, event: RoutingEvent) -> None:
        ...
