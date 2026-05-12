from __future__ import annotations

from typing import Any, Protocol


class ModeHandler(Protocol):
    def build_profile(self, form_state: dict[str, Any], spicy_level: int, effective_style_mode: str) -> dict[str, Any]:
        ...

    def render_prompt_batch(
        self,
        batch: list[dict[str, Any]],
        findings_map: dict[int, list[dict[str, Any]]],
        form_state: dict[str, Any],
        spicy_level: int,
        effective_style_mode: str,
        chosen_seed: int,
        user_profile: dict[str, Any],
    ) -> list[dict[str, Any]]:
        ...

    def post_render_batch(self, prompts: list[dict[str, Any]], form_state: dict[str, Any], spicy_level: int) -> list[dict[str, Any]]:
        ...


def get_mode_handler(mode: str) -> ModeHandler:
    if mode == "women":
        from .women import WOMEN_HANDLER

        return WOMEN_HANDLER
    if mode == "men":
        from .men import MEN_HANDLER

        return MEN_HANDLER
    if mode == "couples":
        from .couples import COUPLES_HANDLER

        return COUPLES_HANDLER
    raise ValueError(f"Unsupported mode handler: {mode}")
