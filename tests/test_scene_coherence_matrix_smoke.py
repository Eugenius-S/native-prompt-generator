import json
import threading
import time
from pathlib import Path

import pytest
import requests


DATA_ROOT = Path(__file__).resolve().parents[1] / "backend" / "engine" / "data"
OUTFIT_TAGS = {
    item["id"]: set(item.get("tags", []))
    for item in json.loads((DATA_ROOT / "styling.json").read_text(encoding="utf-8"))["outfit_families"]
}
POSE_TAGS = {
    item["id"]: set(item.get("tags", []))
    for item in json.loads((DATA_ROOT / "pose_bank.json").read_text(encoding="utf-8"))["pose_families"]
}


def start_server():
    from app import PromptGeneratorHandler, ThreadingHTTPServer

    server = ThreadingHTTPServer(("127.0.0.1", 0), PromptGeneratorHandler)
    port = server.server_address[1]

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, port


def wait_bootstrap(port: int):
    response = None
    for _ in range(30):
        try:
            response = requests.get(f"http://127.0.0.1:{port}/api/bootstrap", timeout=2)
            if response.status_code == 200:
                return response
        except requests.RequestException:
            time.sleep(0.1)
    return response


def _assert_pose_task_contract(scene_family_id: str, pose_tags: set[str]) -> None:
    if "bookish" in pose_tags:
        assert scene_family_id == "culture_bookish"
    if "sport_prep" in pose_tags:
        assert scene_family_id in {"wellness_spa", "coastal_pool"}
    if "creative" in pose_tags:
        assert scene_family_id == "creative_gallery"
    if "domestic" in pose_tags:
        assert scene_family_id in {"residential_luxury", "hospitality_suite", "grooming_bath"}
    if "outdoor" in pose_tags:
        assert scene_family_id in {"coastal_pool", "urban_daylight"}


def _assert_outfit_scene_contract(scene_family_id: str, outfit_tags: set[str]) -> None:
    if scene_family_id == "culture_bookish":
        assert "sporty" not in outfit_tags
        assert "swimwear" not in outfit_tags
        assert "pushing_it" not in outfit_tags
    if scene_family_id == "wellness_spa":
        assert "pushing_it" not in outfit_tags
    if scene_family_id in {"nightlife_bar", "nightlife_neon"}:
        assert "sporty" not in outfit_tags
        assert "vacation" not in outfit_tags


MATRIX_CASES = [
    {
        "id": "women_bookish",
        "form_state": {
            "mode": "women",
            "batchSize": 8,
            "debugMode": True,
            "styleMode": "lifestyle",
            "sceneFocus": "bookish",
            "womenSceneFamily": "culture_bookish",
            "antiRepeat": "hard",
            "validationMode": "strict",
        },
        "allowed_scene_families": {"culture_bookish"},
        "banned_outfit_tags": {"sporty", "swimwear", "pushing_it"},
        "banned_pose_tags": {"sport_prep"},
    },
    {
        "id": "women_wellness",
        "form_state": {
            "mode": "women",
            "batchSize": 8,
            "debugMode": True,
            "styleMode": "random",
            "sceneFocus": "wellness",
            "womenSceneFamily": "wellness_spa",
            "antiRepeat": "hard",
            "validationMode": "strict",
        },
        "allowed_scene_families": {"wellness_spa"},
        "banned_outfit_tags": {"pushing_it"},
        "banned_pose_tags": {"bookish"},
    },
    {
        "id": "couples_bookish",
        "form_state": {
            "mode": "couples",
            "personMode": "different_persons",
            "batchSize": 8,
            "debugMode": True,
            "styleMode": "lifestyle",
            "sceneFocus": "bookish",
            "locationStrategy": "exact_theme",
            "exactTheme": "museum",
            "antiRepeat": "hard",
            "validationMode": "strict",
        },
        "allowed_scene_families": {"culture_bookish"},
        "banned_outfit_tags": {"sporty", "swimwear"},
        "banned_pose_tags": {"sport_prep"},
    },
    {
        "id": "couples_nightlife",
        "form_state": {
            "mode": "couples",
            "personMode": "different_persons",
            "batchSize": 8,
            "debugMode": True,
            "styleMode": "nightlife",
            "sceneFocus": "nightlife",
            "locationStrategy": "exact_theme",
            "exactTheme": "cocktail bar",
            "antiRepeat": "hard",
            "validationMode": "strict",
        },
        "allowed_scene_families": {"nightlife_bar", "nightlife_neon"},
        "banned_outfit_tags": {"sporty", "vacation"},
        "banned_pose_tags": {"bookish", "sport_prep"},
    },
    {
        "id": "women_luxury_exact_theme",
        "form_state": {
            "mode": "women",
            "batchSize": 8,
            "debugMode": True,
            "styleMode": "luxury",
            "sceneFocus": "random",
            "locationStrategy": "exact_theme",
            "exactTheme": "hotel suite",
            "antiRepeat": "hard",
            "validationMode": "strict",
        },
        "allowed_scene_families": {"residential_luxury", "hospitality_suite", "grooming_bath"},
        "banned_outfit_tags": {"sporty", "swimwear"},
        "banned_pose_tags": {"sport_prep", "bookish"},
    },
    {
        "id": "women_creative_exact_theme",
        "form_state": {
            "mode": "women",
            "batchSize": 8,
            "debugMode": True,
            "styleMode": "creative_artistic",
            "sceneFocus": "random",
            "locationStrategy": "exact_theme",
            "exactTheme": "art gallery",
            "antiRepeat": "hard",
            "validationMode": "strict",
        },
        "allowed_scene_families": {"creative_gallery"},
        "banned_outfit_tags": {"sporty", "swimwear"},
        "banned_pose_tags": {"bookish", "sport_prep", "domestic"},
    },
    {
        "id": "couples_luxury_exact_theme",
        "form_state": {
            "mode": "couples",
            "personMode": "different_persons",
            "batchSize": 8,
            "debugMode": True,
            "styleMode": "luxury",
            "sceneFocus": "random",
            "locationStrategy": "exact_theme",
            "exactTheme": "hotel lobby",
            "antiRepeat": "hard",
            "validationMode": "strict",
        },
        "allowed_scene_families": {"residential_luxury", "hospitality_suite", "grooming_bath"},
        "banned_outfit_tags": {"sporty", "swimwear", "vacation"},
        "banned_pose_tags": {"bookish", "sport_prep"},
    },
]


@pytest.mark.parametrize("case", MATRIX_CASES, ids=[case["id"] for case in MATRIX_CASES])
def test_scene_coherence_matrix_smoke(case: dict[str, object]):
    server, thread, port = start_server()
    try:
        bootstrap = wait_bootstrap(port)
        assert bootstrap is not None
        assert bootstrap.status_code == 200

        form_state = case["form_state"]
        allowed_scene_families = case["allowed_scene_families"]
        banned_outfit_tags = case["banned_outfit_tags"]
        banned_pose_tags = case["banned_pose_tags"]

        for _ in range(2):
            response = requests.post(
                f"http://127.0.0.1:{port}/api/generate",
                json={"formState": form_state},
                timeout=30,
            )
            assert response.status_code == 200, response.text

            run = response.json()["run"]
            for item in run["prompts"]:
                candidate = item["candidate"]
                scene_family_id = candidate["scene_family_id"]
                outfit_family_id = candidate["outfit_family_id"]
                pose_family_id = candidate["pose_family_id"]

                assert scene_family_id in allowed_scene_families

                outfit_tags = OUTFIT_TAGS[outfit_family_id]
                pose_tags = POSE_TAGS[pose_family_id]

                assert not (outfit_tags & banned_outfit_tags)
                assert not (pose_tags & banned_pose_tags)

                _assert_outfit_scene_contract(scene_family_id, outfit_tags)
                _assert_pose_task_contract(scene_family_id, pose_tags)
    finally:
        server.shutdown()
        thread.join(timeout=1)
