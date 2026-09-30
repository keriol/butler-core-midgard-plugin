from __future__ import annotations

from .contracts import (
    MidgardError,
    MidgardErrorCode,
    MidgardRequest,
    MidgardResponse,
    MidgardResult,
)
from .ports import CoreRequestHandler


class MidgardChannel:
    """Provider-neutral communication seam between Bifröst-facing input and Core."""

    def __init__(self, handler: CoreRequestHandler) -> None:
        self._handler = handler

    async def send(self, request: MidgardRequest) -> MidgardResult:
        validation_error = self._validate(request)
        if validation_error is not None:
            return validation_error

        try:
            result = await self._handler.handle(request)
        except Exception:
            return MidgardError(
                code=MidgardErrorCode.CORE_FAILURE,
                message="The Core-facing handler failed.",
                request_id=request.request_id,
            )

        if result.request_id != request.request_id:
            return MidgardError(
                code=MidgardErrorCode.CORRELATION_MISMATCH,
                message="The response correlation does not match the request.",
                request_id=request.request_id,
            )

        return result

    @staticmethod
    def _validate(request: MidgardRequest) -> MidgardError | None:
        if not request.request_id.strip():
            return MidgardError(
                code=MidgardErrorCode.INVALID_REQUEST,
                message="request_id must not be empty.",
            )

        if not request.message.strip():
            return MidgardError(
                code=MidgardErrorCode.INVALID_REQUEST,
                message="message must not be empty.",
                request_id=request.request_id,
            )

        return None
