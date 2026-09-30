from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class MidgardErrorCode(str, Enum):
    INVALID_REQUEST = "invalid_request"
    CORRELATION_MISMATCH = "correlation_mismatch"
    CORE_FAILURE = "core_failure"


@dataclass(frozen=True, slots=True)
class SpeakerContext:
    speaker_id: str
    persistent: bool = False
    call_me: str | None = None
    language: str | None = None


@dataclass(frozen=True, slots=True)
class MidgardRequest:
    request_id: str
    message: str
    target_butler_name: str | None = None
    speaker: SpeakerContext | None = None


@dataclass(frozen=True, slots=True)
class MidgardResponse:
    request_id: str
    response: str


@dataclass(frozen=True, slots=True)
class MidgardError:
    code: MidgardErrorCode
    message: str
    request_id: str | None = None


MidgardResult = MidgardResponse | MidgardError
