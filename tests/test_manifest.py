from __future__ import annotations

from butler_midgard import (
    ButlerDescriptor,
    CallableDescriptor,
    CoreStackDescriptor,
    DependencyDescriptor,
    EntityDescriptor,
    MidgardManifestProjector,
    PluginDescriptor,
    ReadinessDescriptor,
)


class FakeDescriptorSource:
    def __init__(self, descriptor: ButlerDescriptor) -> None:
        self._descriptor = descriptor

    @property
    def butler_descriptor(self) -> ButlerDescriptor:
        return self._descriptor


def test_manifest_keeps_core_plugins_shared_and_butler_metadata_local() -> None:
    core = CoreStackDescriptor(
        version="1.2.3",
        plugins=(
            PluginDescriptor(
                name="routing-plugin",
                version="0.4.0",
                available=True,
            ),
            PluginDescriptor(
                name="observability-plugin",
                version="0.7.0",
                available=True,
            ),
        ),
    )

    butler = ButlerDescriptor(
        canonical_name="Butler-A",
        aliases=("A",),
        description="Example Butler",
        version="2.0.0",
        available=True,
        asgard_version="0.1.0",
        entities=(
            EntityDescriptor(
                name="Example Entity",
                description="Example domain owner",
                available=True,
                methods=(
                    CallableDescriptor(
                        name="inspect",
                        description="Inspect current state",
                        available=True,
                        dependencies=(
                            DependencyDescriptor(
                                name="shared-provider",
                                version="3.0.0",
                            ),
                        ),
                    ),
                ),
            ),
        ),
        plugins=(
            PluginDescriptor(
                name="butler-local-plugin",
                version="1.0.0",
                readiness=ReadinessDescriptor(
                    state="usable",
                ),
            ),
        ),
    )

    manifest = MidgardManifestProjector(
        core=core,
        butlers=(FakeDescriptorSource(butler),),
    ).snapshot()

    assert manifest.core is core
    assert manifest.core.plugins[0].name == "routing-plugin"
    assert manifest.butlers == (butler,)
    assert manifest.butlers[0].entities[0].methods[0].name == "inspect"
    assert manifest.butlers[0].plugins[0].name == "butler-local-plugin"


def test_manifest_preserves_multiple_asgard_projected_butlers() -> None:
    manifest = MidgardManifestProjector(
        core=CoreStackDescriptor(version="1.0.0"),
        butlers=(
            FakeDescriptorSource(
                ButlerDescriptor(
                    canonical_name="Butler-A",
                    available=True,
                )
            ),
            FakeDescriptorSource(
                ButlerDescriptor(
                    canonical_name="Butler-B",
                    available=False,
                )
            ),
        ),
    ).snapshot()

    assert tuple(
        item.canonical_name
        for item in manifest.butlers
    ) == ("Butler-A", "Butler-B")
    assert manifest.butlers[1].available is False


def test_manifest_does_not_infer_missing_methods_dependencies_or_readiness() -> None:
    descriptor = ButlerDescriptor(
        canonical_name="Butler-A",
        entities=(
            EntityDescriptor(
                name="Minimal Entity",
            ),
        ),
        plugins=(
            PluginDescriptor(
                name="minimal-plugin",
                version="0.1.0",
            ),
        ),
    )

    manifest = MidgardManifestProjector(
        core=CoreStackDescriptor(version="1.0.0"),
        butlers=(FakeDescriptorSource(descriptor),),
    ).snapshot()

    entity = manifest.butlers[0].entities[0]
    plugin = manifest.butlers[0].plugins[0]

    assert entity.methods == ()
    assert entity.dependencies == ()
    assert entity.readiness is None
    assert plugin.dependencies == ()
    assert plugin.readiness is None
