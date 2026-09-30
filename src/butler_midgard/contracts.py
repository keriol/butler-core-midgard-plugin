from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class MidgardErrorCode(str, Enum):
    INVALID_REQUEST = "invalid_request"
    TARGET_REQUIRED = "target_required"
    UNKNOWN_TARGET = "unknown_target"
    TARGET_UNAVAILABLE = "target_unavailable"
    AMBIGUOUS_TARGET = "ambiguous_target"
    CORRELATION_MISMATCH = "correlation_mismatch"
    SOURCE_IDENTITY_MISMATCH = "source_identity_mismatch"
    TARGET_FAILURE = "target_failure"
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
    source_butler_name: str | None = None


@dataclass(frozen=True, slots=True)
class MidgardError:
    code: MidgardErrorCode
    message: str
    request_id: str | None = None


MidgardResult = MidgardResponse | MidgardError
