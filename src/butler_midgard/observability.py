from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RoutingEventType(str, Enum):
    RECEIVED = "midgard.route.received"
    SELECTED = "midgard.route.selected"
    COMPLETED = "midgard.route.completed"
    FAILED = "midgard.route.failed"


@dataclass(frozen=True, slots=True)
class RoutingEvent:
    event_type: RoutingEventType
    request_id: str
    target_butler_name: str | None = None
    source_butler_name: str | None = None
    reason: str | None = None


class NullMidgardObserver:
    def record(self, event: RoutingEvent) -> None:
        return None
