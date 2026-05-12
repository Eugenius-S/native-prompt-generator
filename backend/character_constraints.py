from __future__ import annotations

from typing import Any, Mapping


_CHARACTER_PREFIXES = (
    "character read:",
    "character:",
    "character note:",
    "character energy:",
)


def normalize_character_constraint(value: str) -> str:
    text = " ".join(str(value or "").split()).strip(" ,.;:-")
    if not text:
        return ""

    lowered = text.lower()
    for prefix in _CHARACTER_PREFIXES:
        if lowered.startswith(prefix):
            text = text[len(prefix) :].strip(" ,.;:-")
            break

    return text


def build_character_constraint_segment(value: str) -> str:
    normalized = normalize_character_constraint(value)
    if not normalized:
        return ""
    return f"Character read: {normalized}"


def resolve_character_constraint_segment(
    candidate: Mapping[str, Any] | None = None,
    character_constraint: str = "",
) -> str:
    if candidate is not None:
        segment = str(candidate.get("character_constraint_segment", "") or "").strip()
        if segment:
            return segment
        character_constraint = str(candidate.get("character_constraint", "") or character_constraint)
    return build_character_constraint_segment(character_constraint)
