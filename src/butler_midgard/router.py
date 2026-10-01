from __future__ import annotations

from collections.abc import Iterable

from butler_core import (
    NullTracer,
    TraceContext,
    TraceEvent,
    TraceLevel,
    TraceSeverity,
    TraceStatus,
    Tracer,
    current_trace_context,
    safe_emit,
)

from .contracts import (
    ClientNotification,
    ClientNotificationKind,
    ButlerDirectoryEntry,
    MidgardError,
    MidgardErrorCode,
    MidgardRequest,
    MidgardResult,
)
from .ports import AsgardTarget


class MidgardRouter:
    """Route requests between Butler universes through Butler-owned Asgards."""

    def __init__(
        self,
        targets: Iterable[AsgardTarget],
        *,
        tracer: Tracer | None = None,
        documentation_url: str | None = None,
    ) -> None:
        self._targets = tuple(targets)
        self._tracer = tracer or NullTracer()
        self._documentation_url = documentation_url

    @property
    def visible_butlers(self) -> tuple[ButlerDirectoryEntry, ...]:
        return tuple(
            ButlerDirectoryEntry(
                canonical_name=target.butler_name,
                aliases=tuple(target.nicknames),
                available=target.available,
            )
            for target in self._targets
        )

    @property
    def visible_butler_names(self) -> tuple[str, ...]:
        """Backward-compatible projection of visible canonical identities."""
        return tuple(entry.canonical_name for entry in self.visible_butlers)

    async def route(self, request: MidgardRequest) -> MidgardResult:
        context = current_trace_context() or TraceContext.root()

        self._emit(
            context,
            operation="midgard.route.received",
            message="Midgard routing request received.",
            status=TraceStatus.NORMAL,
            level=TraceLevel.ACTIVITY,
            request=request,
        )

        target_name = request.target_butler_name
        if target_name is None or not target_name.strip():
            return self._fail(
                context,
                request,
                MidgardErrorCode.TARGET_REQUIRED,
                "A target Butler name is required.",
            )

        matches = tuple(
            target
            for target in self._targets
            if target.matches_butler_name(target_name)
        )

        if not matches:
            return self._unavailable(
                context,
                request,
                MidgardErrorCode.BUTLER_NOT_FOUND,
                "The requested Butler could not be found.",
            )

        if len(matches) > 1:
            return self._fail(
                context,
                request,
                MidgardErrorCode.AMBIGUOUS_TARGET,
                "More than one Asgard recognizes the requested Butler identity.",
            )

        target = matches[0]
        if not target.available:
            return self._unavailable(
                context,
                request,
                MidgardErrorCode.TARGET_UNAVAILABLE,
                "The requested Butler is currently unavailable.",
                source_butler_name=target.butler_name,
            )

        self._emit(
            context,
            operation="midgard.route.selected",
            message="Midgard selected a Butler-owned Asgard.",
            status=TraceStatus.SUCCESS,
            level=TraceLevel.ACTIVITY,
            request=request,
            source_butler_name=target.butler_name,
        )

        try:
            result = await target.handle(request)
        except Exception:
            return self._unavailable(
                context,
                request,
                MidgardErrorCode.TARGET_FAILURE,
                "The requested Butler did not answer.",
                source_butler_name=target.butler_name,
            )

        if result.request_id != request.request_id:
            return self._fail(
                context,
                request,
                MidgardErrorCode.CORRELATION_MISMATCH,
                "The response correlation does not match the request.",
                source_butler_name=target.butler_name,
            )

        if isinstance(result, MidgardError):
            self._emit(
                context,
                operation="midgard.route.failed",
                message="The selected Butler returned a structured routing failure.",
                status=TraceStatus.ERROR,
                severity=TraceSeverity.DEGRADED,
                level=TraceLevel.OPERATIONAL,
                request=request,
                source_butler_name=target.butler_name,
                reason=result.code.value,
            )
            return result

        if result.source_butler_name != target.butler_name:
            return self._fail(
                context,
                request,
                MidgardErrorCode.SOURCE_IDENTITY_MISMATCH,
                "The response Butler identity does not match the selected Asgard.",
                source_butler_name=target.butler_name,
            )

        self._emit(
            context,
            operation="midgard.route.completed",
            message="Midgard routing completed.",
            status=TraceStatus.SUCCESS,
            level=TraceLevel.ACTIVITY,
            request=request,
            source_butler_name=result.source_butler_name,
        )
        return result

    def _unavailable(
        self,
        context: TraceContext,
        request: MidgardRequest,
        code: MidgardErrorCode,
        message: str,
        *,
        source_butler_name: str | None = None,
    ) -> MidgardError:
        return self._fail(
            context,
            request,
            code,
            message,
            source_butler_name=source_butler_name,
            notification=ClientNotification(
                kind=ClientNotificationKind.BUTLER_UNAVAILABLE,
                documentation_url=self._documentation_url,
            ),
        )

    def _fail(
        self,
        context: TraceContext,
        request: MidgardRequest,
        code: MidgardErrorCode,
        message: str,
        *,
        source_butler_name: str | None = None,
        notification: ClientNotification | None = None,
    ) -> MidgardError:
        self._emit(
            context,
            operation="midgard.route.failed",
            message="Midgard routing failed.",
            status=TraceStatus.ERROR,
            severity=TraceSeverity.DEGRADED,
            level=TraceLevel.OPERATIONAL,
            request=request,
            source_butler_name=source_butler_name,
            reason=code.value,
        )
        return MidgardError(
            code=code,
            message=message,
            request_id=request.request_id or None,
            notification=notification,
        )

    def _emit(
        self,
        context: TraceContext,
        *,
        operation: str,
        message: str,
        status: TraceStatus,
        request: MidgardRequest,
        level: TraceLevel,
        severity: TraceSeverity = TraceSeverity.NORMAL,
        source_butler_name: str | None = None,
        reason: str | None = None,
    ) -> None:
        attributes: dict[str, str] = {
            "request_id": request.request_id,
        }
        if request.target_butler_name:
            attributes["target_butler_name"] = request.target_butler_name
        if source_butler_name:
            attributes["source_butler_name"] = source_butler_name
        if reason:
            attributes["reason"] = reason

        safe_emit(
            self._tracer,
            TraceEvent(
                context=context,
                component="midgard",
                operation=operation,
                message=message,
                level=level,
                status=status,
                severity=severity,
                attributes=attributes,
            ),
        )
