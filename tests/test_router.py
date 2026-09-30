from __future__ import annotations

import pytest

from butler_midgard import (
    MidgardError,
    MidgardErrorCode,
    MidgardRequest,
    MidgardResponse,
    MidgardRouter,
    RoutingEvent,
    RoutingEventType,
)


class FakeAsgard:
    def __init__(
        self,
        butler_name: str,
        *,
        available: bool = True,
        response_name: str | None = None,
    ) -> None:
        self._butler_name = butler_name
        self._available = available
        self._response_name = response_name or butler_name
        self.received: list[MidgardRequest] = []

    @property
    def butler_name(self) -> str:
        return self._butler_name

    @property
    def available(self) -> bool:
        return self._available

    async def handle(self, request: MidgardRequest) -> MidgardResponse:
        self.received.append(request)
        return MidgardResponse(
            request_id=request.request_id,
            response=f"{self.butler_name}: {request.message}",
            source_butler_name=self._response_name,
        )


class RecordingObserver:
    def __init__(self) -> None:
        self.events: list[RoutingEvent] = []

    def record(self, event: RoutingEvent) -> None:
        self.events.append(event)


@pytest.mark.asyncio
async def test_routes_to_matching_asgard_and_preserves_source_identity() -> None:
    butler_a = FakeAsgard("Butler-A")
    butler_b = FakeAsgard("Butler-B")
    observer = RecordingObserver()
    router = MidgardRouter([butler_a, butler_b], observer=observer)

    result = await router.route(
        MidgardRequest(
            request_id="req-1",
            message="hello",
            target_butler_name="Butler-B",
        )
    )

    assert result == MidgardResponse(
        request_id="req-1",
        response="Butler-B: hello",
        source_butler_name="Butler-B",
    )
    assert butler_a.received == []
    assert len(butler_b.received) == 1
    assert [event.event_type for event in observer.events] == [
        RoutingEventType.RECEIVED,
        RoutingEventType.SELECTED,
        RoutingEventType.COMPLETED,
    ]
    assert observer.events[-1].source_butler_name == "Butler-B"


@pytest.mark.asyncio
async def test_unknown_target_is_stable_error_and_observed() -> None:
    observer = RecordingObserver()
    router = MidgardRouter([FakeAsgard("Butler-A")], observer=observer)

    result = await router.route(
        MidgardRequest(
            request_id="req-2",
            message="hello",
            target_butler_name="Missing",
        )
    )

    assert result == MidgardError(
        code=MidgardErrorCode.UNKNOWN_TARGET,
        message="The requested Butler is not visible to Midgard.",
        request_id="req-2",
    )
    assert observer.events[-1].event_type is RoutingEventType.FAILED
    assert observer.events[-1].reason == "unknown_target"


@pytest.mark.asyncio
async def test_unavailable_target_is_rejected() -> None:
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


@pytest.mark.asyncio
async def test_duplicate_asgard_identity_is_ambiguous() -> None:
    first = FakeAsgard("Butler-A")
    second = FakeAsgard("Butler-A")
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
async def test_observer_failure_does_not_break_routing() -> None:
    class BrokenObserver:
        def record(self, event: RoutingEvent) -> None:
            raise RuntimeError("observer down")

    router = MidgardRouter(
        [FakeAsgard("Butler-A")],
        observer=BrokenObserver(),
    )

    result = await router.route(
        MidgardRequest(
            request_id="req-8",
            message="hello",
            target_butler_name="Butler-A",
        )
    )

    assert isinstance(result, MidgardResponse)
    assert result.source_butler_name == "Butler-A"
