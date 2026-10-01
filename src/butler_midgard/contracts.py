from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class MidgardErrorCode(str, Enum):
    INVALID_REQUEST = "invalid_request"
    TARGET_REQUIRED = "target_required"
    BUTLER_NOT_FOUND = "butler_not_found"
    TARGET_UNAVAILABLE = "target_unavailable"
    AMBIGUOUS_TARGET = "ambiguous_target"
    CORRELATION_MISMATCH = "correlation_mismatch"
    SOURCE_IDENTITY_MISMATCH = "source_identity_mismatch"
    TARGET_FAILURE = "target_failure"
    CORE_FAILURE = "core_failure"


class ClientNotificationKind(str, Enum):
    BUTLER_UNAVAILABLE = "butler_unavailable"


class ClientNotificationPresentation(str, Enum):
    SYSTEM_NEUTRAL = "system_neutral"


@dataclass(frozen=True, slots=True)
class ClientNotification:
    kind: ClientNotificationKind
    presentation: ClientNotificationPresentation = (
        ClientNotificationPresentation.SYSTEM_NEUTRAL
    )
    documentation_url: str | None = None


@dataclass(frozen=True, slots=True)
class SpeakerContext:
    speaker_id: str
    persistent: bool = False
    call_me: str | None = None
    language: str | None = None


@dataclass(frozen=True, slots=True)
class ButlerDirectoryEntry:
    canonical_name: str
    aliases: tuple[str, ...] = ()
    available: bool = True


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
    notification: ClientNotification | None = None


MidgardResult = MidgardResponse | MidgardError
