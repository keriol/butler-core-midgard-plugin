from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DependencyDescriptor:
    name: str
    version: str | None = None


@dataclass(frozen=True, slots=True)
class ReadinessDescriptor:
    state: str
    reason_code: str | None = None


@dataclass(frozen=True, slots=True)
class CallableDescriptor:
    name: str
    description: str = ""
    available: bool = True
    readiness: ReadinessDescriptor | None = None
    dependencies: tuple[DependencyDescriptor, ...] = ()


@dataclass(frozen=True, slots=True)
class EntityDescriptor:
    name: str
    description: str = ""
    available: bool = True
    readiness: ReadinessDescriptor | None = None
    methods: tuple[CallableDescriptor, ...] = ()
    dependencies: tuple[DependencyDescriptor, ...] = ()


@dataclass(frozen=True, slots=True)
class PluginDescriptor:
    name: str
    version: str
    description: str = ""
    available: bool = True
    readiness: ReadinessDescriptor | None = None
    dependencies: tuple[DependencyDescriptor, ...] = ()


@dataclass(frozen=True, slots=True)
class ButlerDescriptor:
    canonical_name: str
    aliases: tuple[str, ...] = ()
    description: str = ""
    version: str | None = None
    available: bool = True
    asgard_version: str | None = None
    profile_picture_data_uri: str | None = None
    entities: tuple[EntityDescriptor, ...] = ()
    plugins: tuple[PluginDescriptor, ...] = ()


@dataclass(frozen=True, slots=True)
class CoreStackDescriptor:
    version: str
    plugins: tuple[PluginDescriptor, ...] = ()


@dataclass(frozen=True, slots=True)
class MidgardNodeManifest:
    core: CoreStackDescriptor
    butlers: tuple[ButlerDescriptor, ...] = ()
