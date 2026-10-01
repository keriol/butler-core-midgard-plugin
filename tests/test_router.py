from __future__ import annotations

import pytest
from butler_core import TraceEvent

from butler_midgard import (
    ButlerDirectoryEntry,
    ClientNotificationKind,
    ClientNotificationPresentation,
    MidgardError,
    MidgardErrorCode,
    MidgardRequest,
    MidgardResponse,
    MidgardRouter,
)


class FakeAsgard:
    def __init__(
        self,
        butler_name: str,
        *,
        available: bool = True,
        response_name: str | None = None,
        aliases: tuple[str, ...] = (),
    ) -> None:
        self._butler_name = butler_name
        self._available = available
        self._response_name = response_name or butler_name
        self._aliases = aliases
        self.received: list[MidgardRequest] = []
        self.name_queries: list[str] = []

    @property
    def butler_name(self) -> str:
        return self._butler_name

    @property
    def available(self) -> bool:
        return self._available

    @property
    def nicknames(self) -> tuple[str, ...]:
        return self._aliases

    def matches_butler_name(self, requested_name: str) -> bool:
        self.name_queries.append(requested_name)
        return requested_name == self.butler_name or requested_name in self._aliases

    async def handle(self, request: MidgardRequest) -> MidgardResponse:
        self.received.append(request)
        return MidgardResponse(
            request_id=request.request_id,
            response=f"{self.butler_name}: {request.message}",
            source_butler_name=self._response_name,
        )


class RecordingTracer:
    def __init__(self) -> None:
        self.events: list[TraceEvent] = []

    def emit(self, event: TraceEvent) -> None:
        self.events.append(event)


@pytest.mark.asyncio
async def test_midgard_asks_asgards_and_emits_core_georges_trace() -> None:
    butler_a = FakeAsgard("Butler-A")
    butler_b = FakeAsgard("Butler-B")
    tracer = RecordingTracer()
    router = MidgardRouter([butler_a, butler_b], tracer=tracer)

    result = await router.route(
        MidgardRequest(
            request_id="req-1",
            message="hello",
            target_butler_name="Butler-B",
        )
    )

    assert butler_a.name_queries == ["Butler-B"]
    assert butler_b.name_queries == ["Butler-B"]
    assert butler_a.received == []
    assert len(butler_b.received) == 1
    assert result == MidgardResponse(
        request_id="req-1",
        response="Butler-B: hello",
        source_butler_name="Butler-B",
    )
    assert [event.operation for event in tracer.events] == [
        "midgard.route.received",
        "midgard.route.selected",
        "midgard.route.completed",
    ]
    assert len({event.context.trace_id for event in tracer.events}) == 1
    assert tracer.events[-1].attributes["source_butler_name"] == "Butler-B"
    assert all("hello" not in str(event.attributes) for event in tracer.events)


@pytest.mark.asyncio
async def test_all_asgards_say_not_me_returns_butler_not_found_notification() -> None:
    first = FakeAsgard("Butler-A")
    second = FakeAsgard("Butler-B")
    tracer = RecordingTracer()
    router = MidgardRouter(
        [first, second],
        tracer=tracer,
        documentation_url="https://docs.example.test/doctor",
    )

    result = await router.route(
        MidgardRequest(
            request_id="req-2",
            message="private message",
            target_butler_name="Missing",
        )
    )

    assert first.name_queries == ["Missing"]
    assert second.name_queries == ["Missing"]
    assert isinstance(result, MidgardError)
    assert result.code is MidgardErrorCode.BUTLER_NOT_FOUND
    assert result.notification is not None
    assert result.notification.kind is ClientNotificationKind.BUTLER_UNAVAILABLE
    assert (
        result.notification.presentation
        is ClientNotificationPresentation.SYSTEM_NEUTRAL
    )
    assert result.notification.documentation_url == "https://docs.example.test/doctor"
    assert tracer.events[-1].operation == "midgard.route.failed"
    assert tracer.events[-1].attributes["reason"] == "butler_not_found"
    assert all("private message" not in str(event.attributes) for event in tracer.events)


@pytest.mark.asyncio
async def test_offline_matching_butler_returns_same_neutral_notification_kind() -> None:
    router = MidgardRouter([FakeAsgard("Butler-A", available=False)])

    result = await router.route(
        MidgardRequest(
            request_id="req-3",
            message="hello",
            target_butler_name="Butler-A",
        )
    )

    assert isinstance(result, MidgardError)
    assert result.code is MidgardErrorCode.TARGET_UNAVAILABLE
    assert result.notification is not None
    assert result.notification.kind is ClientNotificationKind.BUTLER_UNAVAILABLE


@pytest.mark.asyncio
async def test_duplicate_positive_answers_are_ambiguous() -> None:
    first = FakeAsgard("Butler-A")
    second = FakeAsgard("Different", aliases=("Butler-A",))
    router = MidgardRouter([first, second])

    result = await router.route(
        MidgardRequest(
            request_id="req-4",
            message="hello",
            target_butler_name="Butler-A",
        )
    )

    assert isinstance(result, MidgardError)
    assert result.code is MidgardErrorCode.AMBIGUOUS_TARGET
    assert first.received == []
    assert second.received == []


@pytest.mark.asyncio
async def test_missing_target_has_no_implicit_default() -> None:
    target = FakeAsgard("Butler-A")
    router = MidgardRouter([target])

    result = await router.route(
        MidgardRequest(request_id="req-5", message="hello")
    )

    assert isinstance(result, MidgardError)
    assert result.code is MidgardErrorCode.TARGET_REQUIRED
    assert result.notification is None
    assert target.received == []


@pytest.mark.asyncio
async def test_response_identity_must_come_back_from_selected_asgard() -> None:
    target = FakeAsgard("Butler-A", response_name="Butler-B")
    router = MidgardRouter([target])

    result = await router.route(
        MidgardRequest(
            request_id="req-6",
            message="hello",
            target_butler_name="Butler-A",
        )
    )

    assert isinstance(result, MidgardError)
    assert result.code is MidgardErrorCode.SOURCE_IDENTITY_MISMATCH


@pytest.mark.asyncio
async def test_correlation_mismatch_is_rejected() -> None:
    class WrongCorrelationAsgard(FakeAsgard):
        async def handle(self, request: MidgardRequest) -> MidgardResponse:
            return MidgardResponse(
                request_id="wrong",
                response="wrong",
                source_butler_name=self.butler_name,
            )

    router = MidgardRouter([WrongCorrelationAsgard("Butler-A")])

    result = await router.route(
        MidgardRequest(
            request_id="req-7",
            message="hello",
            target_butler_name="Butler-A",
        )
    )

    assert isinstance(result, MidgardError)
    assert result.code is MidgardErrorCode.CORRELATION_MISMATCH


@pytest.mark.asyncio
async def test_asgard_failure_returns_neutral_butler_unavailable_notification() -> None:
    class BrokenAsgard(FakeAsgard):
        async def handle(self, request: MidgardRequest) -> MidgardResponse:
            raise RuntimeError("offline")

    router = MidgardRouter([BrokenAsgard("Butler-A")])

    result = await router.route(
        MidgardRequest(
            request_id="req-8",
            message="hello",
            target_butler_name="Butler-A",
        )
    )

    assert isinstance(result, MidgardError)
    assert result.code is MidgardErrorCode.TARGET_FAILURE
    assert result.notification is not None
    assert result.notification.kind is ClientNotificationKind.BUTLER_UNAVAILABLE


@pytest.mark.asyncio
async def test_tracer_failure_does_not_break_routing() -> None:
    class BrokenTracer:
        def emit(self, event: TraceEvent) -> None:
            raise RuntimeError("tracer down")

    router = MidgardRouter(
        [FakeAsgard("Butler-A")],
        tracer=BrokenTracer(),
    )

    result = await router.route(
        MidgardRequest(
            request_id="req-9",
            message="hello",
            target_butler_name="Butler-A",
        )
    )

    assert isinstance(result, MidgardResponse)
    assert result.source_butler_name == "Butler-A"


def test_visible_butlers_projects_asgard_owned_identity_aliases_and_availability() -> None:
    router = MidgardRouter(
        [
            FakeAsgard(
                "Butler-A",
                aliases=("A", "Alpha"),
            ),
            FakeAsgard(
                "Butler-B",
                available=False,
                aliases=("B",),
            ),
        ]
    )

    assert router.visible_butlers == (
        ButlerDirectoryEntry(
            canonical_name="Butler-A",
            aliases=("A", "Alpha"),
            available=True,
        ),
        ButlerDirectoryEntry(
            canonical_name="Butler-B",
            aliases=("B",),
            available=False,
        ),
    )
    assert router.visible_butler_names == (
        "Butler-A",
        "Butler-B",
    )
