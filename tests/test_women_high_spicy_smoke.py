from backend import prompt_service
from backend.engine import generator


NEW_HIGH_SPICY_POSE_IDS = {"over_shoulder_arch_stand", "chair_forward_lean", "kneeling_arch_turn"}
NEW_REVEALING_OUTFIT_IDS = {"strappy_cutout_mini_dress"}
NEW_PUSHING_IT_OUTFIT_IDS = {"sheer_mesh_micro_skirt", "bandeau_low_rise_mini"}
LOCAL_SPICY_6_8_POSE_IDS = {
    "table_lean_hips_back",
    "cube_side_twist_knee_hold",
    "counter_hip_lean_collar_touch",
    "bed_side_knees_angled_sweater_hold",
    "bed_kneel_sheet_grip",
    "passenger_seat_twist_seatback_hold",
    "doorframe_arm_overhead_s_curve",
}


def _collect_women_high_spicy_ids(
    monkeypatch,
    *,
    seeds: tuple[int, ...],
    style_mode: str,
    women_scene_family: str,
    scene_focus: str = "random",
):
    monkeypatch.setattr(prompt_service, "append_history", lambda payload: payload)
    monkeypatch.setattr(generator, "_save_memory", lambda _memory: None)

    effective_reveals: set[str] = set()
    outfit_ids: set[str] = set()
    pose_ids: set[str] = set()

    for base_seed in seeds:
        monkeypatch.setattr(prompt_service.random, "randint", lambda _low, _high, chosen=base_seed: chosen)
        run = prompt_service.generate_run(
            {
                "formState": {
                    "mode": "women",
                    "batchSize": 10,
                    "debugMode": True,
                    "styleMode": style_mode,
                    "sceneFocus": scene_focus,
                    "womenSceneFamily": women_scene_family,
                    "spicyLevel": "8",
                    "locationStrategy": "allow_repeats",
                }
            }
        )
        effective_reveals.add(run["debug"]["effectiveOutfitReveal"])
        outfit_ids.update(item["candidate"]["outfit_family_id"] for item in run["prompts"])
        pose_ids.update(item["candidate"]["pose_family_id"] for item in run["prompts"])

    return effective_reveals, outfit_ids, pose_ids


def test_women_high_spicy_random_nightlife_surfaces_new_revealing_outfit(monkeypatch):
    effective_reveals, outfit_ids, _ = _collect_women_high_spicy_ids(
        monkeypatch,
        seeds=(110000111, 220000222, 330000333, 440000444, 550000555),
        style_mode="random",
        women_scene_family="nightlife_bar",
    )

    assert effective_reveals == {"revealing"}
    assert NEW_REVEALING_OUTFIT_IDS <= outfit_ids


def test_women_high_spicy_nightlife_surfaces_new_pushing_it_outfits_and_poses(monkeypatch):
    effective_reveals, outfit_ids, pose_ids = _collect_women_high_spicy_ids(
        monkeypatch,
        seeds=(120000111, 230000222, 340000333, 450000444, 560000555),
        style_mode="nightlife",
        women_scene_family="random",
        scene_focus="nightlife",
    )

    assert effective_reveals == {"pushing_it"}
    assert outfit_ids & NEW_PUSHING_IT_OUTFIT_IDS
    assert pose_ids & (NEW_HIGH_SPICY_POSE_IDS | LOCAL_SPICY_6_8_POSE_IDS)
    assert len(pose_ids & prompt_service.HIGH_SPICY_WOMEN_POSE_IDS) >= 4


def _collect_women_pose_mix(
    monkeypatch,
    *,
    seeds: tuple[int, ...],
    spicy_level: int,
    style_mode: str,
    women_scene_family: str,
    scene_focus: str = "random",
):
    monkeypatch.setattr(prompt_service, "append_history", lambda payload: payload)
    monkeypatch.setattr(generator, "_save_memory", lambda _memory: None)

    active_pose_ids = (
        prompt_service.HIGH_SPICY_WOMEN_REVEALING_POSE_IDS
        if spicy_level == 6
        else prompt_service.HIGH_SPICY_WOMEN_POSE_IDS
    )
    spicy_pose_count = 0
    total_pose_count = 0
    local_pose_ids: set[str] = set()

    for base_seed in seeds:
        monkeypatch.setattr(prompt_service.random, "randint", lambda _low, _high, chosen=base_seed: chosen)
        run = prompt_service.generate_run(
            {
                "formState": {
                    "mode": "women",
                    "batchSize": 10,
                    "debugMode": True,
                    "styleMode": style_mode,
                    "sceneFocus": scene_focus,
                    "womenSceneFamily": women_scene_family,
                    "spicyLevel": str(spicy_level),
                    "locationStrategy": "allow_repeats",
                }
            }
        )
        for item in run["prompts"]:
            pose_id = item["candidate"]["pose_family_id"]
            total_pose_count += 1
            if pose_id in active_pose_ids:
                spicy_pose_count += 1
            if pose_id in LOCAL_SPICY_6_8_POSE_IDS:
                local_pose_ids.add(pose_id)

    return spicy_pose_count, total_pose_count, local_pose_ids


def test_women_spicy_six_prefers_sexy_pose_majority(monkeypatch):
    spicy_pose_count, total_pose_count, local_pose_ids = _collect_women_pose_mix(
        monkeypatch,
        seeds=(610000111, 620000222, 630000333, 640000444, 650000555, 660000666),
        spicy_level=6,
        style_mode="random",
        women_scene_family="random",
    )

    assert spicy_pose_count / total_pose_count >= 0.6
    assert local_pose_ids


def test_women_spicy_eight_prefers_sexy_pose_majority(monkeypatch):
    spicy_pose_count, total_pose_count, local_pose_ids = _collect_women_pose_mix(
        monkeypatch,
        seeds=(810000111, 820000222, 830000333, 840000444, 850000555, 860000666),
        spicy_level=8,
        style_mode="random",
        women_scene_family="random",
    )

    assert spicy_pose_count / total_pose_count >= 0.6
    assert local_pose_ids
