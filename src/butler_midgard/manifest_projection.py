from __future__ import annotations

from collections.abc import Iterable

from .manifest import (
    CoreStackDescriptor,
    MidgardNodeManifest,
)
from .ports import ButlerDescriptorSource


class MidgardManifestProjector:
    """Compose a read-only node manifest from owner-supplied metadata."""

    def __init__(
        self,
        *,
        core: CoreStackDescriptor,
        butlers: Iterable[ButlerDescriptorSource],
    ) -> None:
        self._core = core
        self._butlers = tuple(butlers)

    def snapshot(self) -> MidgardNodeManifest:
        return MidgardNodeManifest(
            core=self._core,
            butlers=tuple(
                source.butler_descriptor
                for source in self._butlers
            ),
        )
