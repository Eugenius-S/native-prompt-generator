from __future__ import annotations

from backend import prompt_service
from backend.engine import generator


NEW_REVEALING_INTERACTION_IDS = {
    "forehead_hold_close_frame",
    "wall_lean_waist_draw",
    "banquette_side_press",
    "lap_seat_turned_in",
    "back_hug_neck_brush",
    "stair_pause_hand_pull",
    "couch_recline_leg_cross",
    "window_hold_side_profile",
}
NEW_PUSHING_IT_INTERACTION_IDS = {
    "near_kiss_wall_frame",
    "cross_lap_seat_editorial",
    "sofa_corner_leg_over_lap",
    "mirror_back_hold_gaze",
    "bed_edge_forehead_draw",
    "standing_v_between_knees",
    "dip_hold_cheek_near",
    "window_silhouette_bodyline",
}
ALL_NEW_INTERACTION_IDS = NEW_REVEALING_INTERACTION_IDS | NEW_PUSHING_IT_INTERACTION_IDS


def _collect_couples_interaction_meta(
    monkeypatch,
    *,
    seeds: tuple[int, ...],
    style_mode: str,
    spicy_level: int,
    scene_focus: str,
    exact_theme: str,
):
    monkeypatch.setattr(prompt_service, "append_history", lambda payload: payload)
    monkeypatch.setattr(generator, "_save_memory", lambda _memory: None)

    interaction_ids: set[str] = set()
    interaction_lanes: set[str] = set()
    scene_families: set[str] = set()

    for base_seed in seeds:
        monkeypatch.setattr(prompt_service.random, "randint", lambda _low, _high, chosen=base_seed: chosen)
        run = prompt_service.generate_run(
            {
                "formState": {
                    "mode": "couples",
                    "personMode": "different_persons",
                    "batchSize": 10,
                    "debugMode": True,
                    "styleMode": style_mode,
                    "sceneFocus": scene_focus,
                    "spicyLevel": str(spicy_level),
                    "locationStrategy": "exact_theme",
                    "exactTheme": exact_theme,
                }
            }
        )
        interaction_ids.update(item["debugMeta"]["coupleInteractionId"] for item in run["prompts"])
        interaction_lanes.update(item["debugMeta"]["coupleInteractionLane"] for item in run["prompts"])
        scene_families.update(item["candidate"]["scene_family_id"] for item in run["prompts"])

    return interaction_ids, interaction_lanes, scene_families


def test_couples_high_spicy_nightlife_surfaces_new_pushing_it_interactions(monkeypatch):
    interaction_ids, interaction_lanes, scene_families = _collect_couples_interaction_meta(
        monkeypatch,
        seeds=(710000111, 720000222, 730000333, 740000444, 750000555),
        style_mode="nightlife",
        spicy_level=8,
        scene_focus="nightlife",
        exact_theme="cocktail bar",
    )

    assert scene_families <= {"nightlife_bar", "nightlife_neon"}
    assert "pushing_it" in interaction_lanes
    assert interaction_ids & NEW_PUSHING_IT_INTERACTION_IDS


def test_couples_mid_high_spicy_romantic_stays_on_revealing_lane(monkeypatch):
    interaction_ids, interaction_lanes, scene_families = _collect_couples_interaction_meta(
        monkeypatch,
        seeds=(760000111, 770000222, 780000333, 790000444, 700000555),
        style_mode="romantic",
        spicy_level=6,
        scene_focus="garden",
        exact_theme="conservatory",
    )

    assert scene_families <= {"courtyard_garden", "garden_conservatory"}
    assert interaction_lanes == {"revealing"}
    assert interaction_ids & NEW_REVEALING_INTERACTION_IDS
    assert not (interaction_ids & NEW_PUSHING_IT_INTERACTION_IDS)


def test_couples_spicy_four_keeps_moderate_safe_interactions(monkeypatch):
    interaction_ids, interaction_lanes, scene_families = _collect_couples_interaction_meta(
        monkeypatch,
        seeds=(801000111, 802000222, 803000333, 804000444),
        style_mode="nightlife",
        spicy_level=4,
        scene_focus="nightlife",
        exact_theme="cocktail bar",
    )

    assert scene_families <= {"nightlife_bar", "nightlife_neon"}
    assert interaction_lanes == {"moderate_safe"}
    assert not (interaction_ids & ALL_NEW_INTERACTION_IDS)
