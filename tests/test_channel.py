from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from butler_midgard import (
    MidgardChannel,
    MidgardError,
    MidgardErrorCode,
    MidgardRequest,
    MidgardResponse,
    SpeakerContext,
)


class EchoCoreHandler:
    async def handle(self, request: MidgardRequest) -> MidgardResponse:
        return MidgardResponse(
            request_id=request.request_id,
            response=f"Echo: {request.message}",
        )


@pytest.mark.asyncio
async def test_channel_preserves_correlation_and_target_metadata() -> None:
    seen: list[MidgardRequest] = []

    class RecordingHandler:
        async def handle(self, request: MidgardRequest) -> MidgardResponse:
            seen.append(request)
            return MidgardResponse(
                request_id=request.request_id,
                response="ok",
            )

    request = MidgardRequest(
        request_id="req-1",
        message="hello",
        target_butler_name="Alfred",
        speaker=SpeakerContext(
            speaker_id="user-1",
            persistent=True,
            call_me="friend",
            language="en",
        ),
    )

    result = await MidgardChannel(RecordingHandler()).send(request)

    assert result == MidgardResponse(request_id="req-1", response="ok")
    assert seen == [request]
    assert seen[0].target_butler_name == "Alfred"


@pytest.mark.asyncio
async def test_channel_returns_structured_core_failure() -> None:
    class FailingHandler:
        async def handle(self, request: MidgardRequest) -> MidgardResponse:
            raise RuntimeError("private implementation detail")

    result = await MidgardChannel(FailingHandler()).send(
        MidgardRequest(request_id="req-2", message="hello")
    )

    assert result == MidgardError(
        code=MidgardErrorCode.CORE_FAILURE,
        message="The Core-facing handler failed.",
        request_id="req-2",
    )
    assert "private implementation detail" not in result.message


@pytest.mark.asyncio
async def test_channel_rejects_correlation_mismatch() -> None:
    class WrongCorrelationHandler:
        async def handle(self, request: MidgardRequest) -> MidgardResponse:
            return MidgardResponse(
                request_id="wrong-id",
                response="wrong",
            )

    result = await MidgardChannel(WrongCorrelationHandler()).send(
        MidgardRequest(request_id="req-3", message="hello")
    )

    assert result == MidgardError(
        code=MidgardErrorCode.CORRELATION_MISMATCH,
        message="The response correlation does not match the request.",
        request_id="req-3",
    )


@pytest.mark.asyncio
async def test_channel_validates_request_before_handler() -> None:
    called = False

    class Handler:
        async def handle(self, request: MidgardRequest) -> MidgardResponse:
            nonlocal called
            called = True
            return MidgardResponse(request_id=request.request_id, response="no")

    result = await MidgardChannel(Handler()).send(
        MidgardRequest(request_id="req-4", message="   ")
    )

    assert called is False
    assert result == MidgardError(
        code=MidgardErrorCode.INVALID_REQUEST,
        message="message must not be empty.",
        request_id="req-4",
    )


def test_contracts_are_immutable() -> None:
    request = MidgardRequest(request_id="req-5", message="hello")

    with pytest.raises(FrozenInstanceError):
        request.message = "changed"  # type: ignore[misc]
