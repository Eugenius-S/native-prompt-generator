from backend.services import scoring


def _candidate(*, pose_family_id: str, camera_framing_id: str) -> dict[str, str]:
    return {
        "pose_family_id": pose_family_id,
        "camera_framing_id": camera_framing_id,
    }


def test_same_person_visual_diversity_score_prefers_varied_pose_and_framing_mix() -> None:
    rigid_batch = [
        _candidate(pose_family_id="standing_three_quarter", camera_framing_id="waist_up"),
        _candidate(pose_family_id="wall_lean", camera_framing_id="waist_up"),
        _candidate(pose_family_id="cowboy_shot_stance", camera_framing_id="cowboy_shot"),
        _candidate(pose_family_id="standing_three_quarter", camera_framing_id="cowboy_shot"),
        _candidate(pose_family_id="wall_lean", camera_framing_id="waist_up"),
        _candidate(pose_family_id="standing_three_quarter", camera_framing_id="cowboy_shot"),
    ]
    varied_batch = [
        _candidate(pose_family_id="standing_three_quarter", camera_framing_id="waist_up"),
        _candidate(pose_family_id="chair_sideways_pose", camera_framing_id="knee_up"),
        _candidate(pose_family_id="backwards_chair_pose", camera_framing_id="full_body"),
        _candidate(pose_family_id="side_lying_lounge", camera_framing_id="ankle_up"),
        _candidate(pose_family_id="stairs_seated", camera_framing_id="cowboy_shot"),
        _candidate(pose_family_id="slow_walk", camera_framing_id="head_and_shoulders"),
    ]

    assert scoring._same_person_visual_diversity_score(varied_batch) > scoring._same_person_visual_diversity_score(rigid_batch)
