from __future__ import annotations

from datetime import datetime
from typing import Any

from backend.modes.registry import get_mode_handler
from backend.forms.constants import ALLOWED_MODES
from backend.prompt_service import infer_theme_style_mode, merged_form_state, resolve_runtime_controls
from backend.services import batch_selection
from backend.services.debug_summary import _summarize_debug
from backend.storage import append_history


def _render_mode_prompts(
    form_state: dict[str, Any],
    spicy_level: int,
    use_recent_batch_rules: bool,
    use_memory_rules: bool,
    effective_style_mode: str,
) -> list[dict[str, Any]]:
    handler = get_mode_handler(form_state["mode"])
    user_profile = handler.build_profile(form_state, spicy_level, effective_style_mode)
    batch, findings_map, chosen_seed = batch_selection._best_batch(form_state, spicy_level, use_recent_batch_rules, use_memory_rules)
    prompts = handler.render_prompt_batch(
        batch,
        findings_map,
        form_state,
        spicy_level,
        effective_style_mode,
        chosen_seed,
        user_profile,
    )
    return handler.post_render_batch(prompts, form_state, spicy_level)


def generate_run(form_payload: dict[str, Any] | None) -> dict[str, Any]:
    form_state = merged_form_state(form_payload)
    if form_state["mode"] not in ALLOWED_MODES:
        raise ValueError("Unsupported mode.")
    spicy_level, use_recent_batch_rules, use_memory_rules, effective_location_strategy, effective_anti_repeat = resolve_runtime_controls(form_state)
    effective_style_mode = infer_theme_style_mode(form_state)
    prompts = _render_mode_prompts(
        form_state,
        spicy_level,
        use_recent_batch_rules,
        use_memory_rules,
        effective_style_mode,
    )
    run_payload = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "formState": form_state,
        "outputText": "\n".join(item["prompt"] for item in prompts),
        "prompts": prompts,
        "debug": _summarize_debug(prompts, form_state, spicy_level, effective_location_strategy, effective_anti_repeat, effective_style_mode),
    }
    return append_history(run_payload)
