from __future__ import annotations

from collections.abc import Iterable

from .contracts import (
    MidgardError,
    MidgardErrorCode,
    MidgardRequest,
    MidgardResponse,
    MidgardResult,
)
from .observability import NullMidgardObserver, RoutingEvent, RoutingEventType
from .ports import AsgardTarget, MidgardObserver


class MidgardRouter:
    """Route requests between Butler universes by Asgard-declared identity."""

    def __init__(
        self,
        targets: Iterable[AsgardTarget],
        *,
        observer: MidgardObserver | None = None,
    ) -> None:
        self._targets = tuple(targets)
        self._observer = observer or NullMidgardObserver()

    @property
    def visible_butler_names(self) -> tuple[str, ...]:
        return tuple(target.butler_name for target in self._targets)

    async def route(self, request: MidgardRequest) -> MidgardResult:
        self._record(
            RoutingEvent(
                event_type=RoutingEventType.RECEIVED,
                request_id=request.request_id,
                target_butler_name=request.target_butler_name,
            )
        )

        target_name = request.target_butler_name
        if target_name is None or not target_name.strip():
            return self._fail(
                request,
                MidgardErrorCode.TARGET_REQUIRED,
                "A target Butler name is required.",
            )

        matches = tuple(
            target for target in self._targets if target.butler_name == target_name
        )

        if not matches:
            return self._fail(
                request,
                MidgardErrorCode.UNKNOWN_TARGET,
                "The requested Butler is not visible to Midgard.",
            )

        if len(matches) > 1:
            return self._fail(
                request,
                MidgardErrorCode.AMBIGUOUS_TARGET,
                "More than one Asgard declares the requested Butler identity.",
            )

        target = matches[0]
        if not target.available:
            return self._fail(
                request,
                MidgardErrorCode.TARGET_UNAVAILABLE,
                "The requested Butler is currently unavailable.",
            )

        self._record(
            RoutingEvent(
                event_type=RoutingEventType.SELECTED,
                request_id=request.request_id,
                target_butler_name=target_name,
                source_butler_name=target.butler_name,
            )
        )

        try:
            result = await target.handle(request)
        except Exception:
            return self._fail(
                request,
                MidgardErrorCode.TARGET_FAILURE,
                "The selected Butler ingress failed.",
                source_butler_name=target.butler_name,
            )

        if result.request_id != request.request_id:
            return self._fail(
                request,
                MidgardErrorCode.CORRELATION_MISMATCH,
                "The response correlation does not match the request.",
                source_butler_name=target.butler_name,
            )

        if isinstance(result, MidgardError):
            self._record(
                RoutingEvent(
                    event_type=RoutingEventType.FAILED,
                    request_id=request.request_id,
                    target_butler_name=target_name,
                    source_butler_name=target.butler_name,
                    reason=result.code.value,
                )
            )
            return result

        if result.source_butler_name != target.butler_name:
            return self._fail(
                request,
                MidgardErrorCode.SOURCE_IDENTITY_MISMATCH,
                "The response Butler identity does not match the selected Asgard.",
                source_butler_name=target.butler_name,
            )

        self._record(
            RoutingEvent(
                event_type=RoutingEventType.COMPLETED,
                request_id=request.request_id,
                target_butler_name=target_name,
                source_butler_name=result.source_butler_name,
            )
        )
        return result

    def _fail(
        self,
        request: MidgardRequest,
        code: MidgardErrorCode,
        message: str,
        *,
        source_butler_name: str | None = None,
    ) -> MidgardError:
        self._record(
            RoutingEvent(
                event_type=RoutingEventType.FAILED,
                request_id=request.request_id,
                target_butler_name=request.target_butler_name,
                source_butler_name=source_butler_name,
                reason=code.value,
            )
        )
        return MidgardError(
            code=code,
            message=message,
            request_id=request.request_id or None,
        )

    def _record(self, event: RoutingEvent) -> None:
        try:
            self._observer.record(event)
        except Exception:
            # Observability must never become an execution dependency.
            pass
