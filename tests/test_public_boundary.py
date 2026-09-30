from __future__ import annotations

from pathlib import Path


FORBIDDEN_TERMS = (
    "homeassistant.",
    "switch.",
    "sensor.",
    "ALFRED_ASGARD_TOKEN",
    "keriolhome",
)


def test_source_does_not_contain_private_or_runtime_specific_terms() -> None:
    root = Path(__file__).parents[1]
    paths = list((root / "src").rglob("*.py")) + [
        root / "README.md",
        root / "docs" / "architecture.md",
    ]

    text = "\n".join(path.read_text(encoding="utf-8") for path in paths)

    for term in FORBIDDEN_TERMS:
        assert term not in text
