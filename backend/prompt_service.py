from __future__ import annotations

import random
import re
from collections import Counter
from datetime import datetime
import math
from typing import Any

from .legacy_bridge import preview_male_identities
from .engine import generator
from .engine.repair import repair_candidate
from .engine.validator import load_rule_bank, validate_candidate
from .forms.constants import ALLOWED_MODES
from .forms import normalizer as form_normalizer
from .forms import runtime_controls as form_runtime_controls
from .forms import user_profile as form_user_profile
from .options import DEFAULT_FORM_STATE, DISABLED_FIELDS, ENABLED_FIELDS, UI_OPTIONS
from .services import postprocess, scoring
from .storage import append_history, delete_preset, list_history, list_presets, save_preset


ALLOWED_PERSON_MODES = {"different_persons", "same_person"}
ALLOWED_APPEARANCE_MODES = {"generated", "custom"}
ALLOWED_ANTI_REPEAT_MODES = {"low", "normal", "hard", "brutal"}
ALLOWED_VALIDATION_MODES = {"loose", "normal", "strict"}
ALLOWED_LOCATION_STRATEGIES = {"random", "fresh_only", "allow_repeats", "exact_theme"}
ALLOWED_OUTFIT_REVEAL_MODES = {"random", "reserved", "balanced", "revealing", "pushing_it"}
ALLOWED_HAIR_LENGTH_MODES = {"random", "short", "medium", "long"}
ALLOWED_SCENE_FOCUS_MODES = {"random", "urban", "luxury", "bookish", "garden", "coastal", "nightlife", "studio", "creative", "wellness", "sporty"}
ALLOWED_WOMEN_SCENE_FAMILIES = {
    "random",
    "culture_bookish",
    "residential_luxury",
    "hospitality_suite",
    "grooming_bath",
    "courtyard_garden",
    "garden_conservatory",
    "coastal_pool",
    "coastal_boardwalk",
    "nightlife_bar",
    "nightlife_neon",
    "studio",
    "creative_gallery",
    "wellness_spa",
    "urban_daylight",
}
ALLOWED_MALE_HAIRSTYLE_MODES = {
    "random",
    "custom",
    "male_clean_side_part",
    "male_textured_crop",
    "male_medium_pushback",
    "male_soft_quiff",
    "male_wavy_brushback",
}
ALLOWED_MALE_GROOMING_CONTROLS = {
    "random",
    "clean_shaven",
    "light_stubble",
    "trimmed_beard",
}
ALLOWED_MALE_OUTFIT_CONTROLS = {
    "random",
    "studio",
    "lifestyle",
    "luxury",
    "old_money",
    "romantic",
    "vacation",
    "sport",
    "fitness",
    "nightlife",
    "cultural_bookish",
    "creative_artistic",
    "urban_day",
    "coastal",
    "cosplay",
    "fantasy",
}
MALE_OUTFIT_CONTROL_ALIASES = {
    "male_open_collar_trousers": "luxury",
    "male_fineknit_trousers": "old_money",
    "male_track_jacket_joggers": "sport",
    "male_relaxed_overshirt_trousers": "lifestyle",
    "male_dark_shirt_trousers": "nightlife",
    "male_black_polo_trousers": "nightlife",
    "male_linen_pleated_trousers": "coastal",
    "male_blazer_knit_trousers": "old_money",
}
ALLOWED_HAIRSTYLE_MODES = {
    "random",
    "custom",
    "soft_waves",
    "sleek_bob",
    "high_ponytail",
    "side_braid",
    "natural_curls",
    "shoulder_blowout",
    "messy_bun",
    "polished_low_bun",
    "soft_half_up",
    "tucked_behind_ears_blowout",
    "long_straight",
    "blunt_bob",
}
ALLOWED_HAIR_COLOR_CONTROLS = {
    "random",
    "custom",
    "black",
    "dark_brown",
    "brown",
    "light_brown",
    "blonde",
    "dark_blonde",
    "red_ginger",
    "auburn",
    "gray_silver",
}
ALLOWED_MAKEUP_CONTROLS = {
    "random",
    "natural_pretty",
    "clean_minimal",
    "fresh_barely_there",
    "groomed_daylight_soft",
    "rosy_polished_minimal",
    "soft_glam_clean",
    "glossy_soft_glam",
    "night_out_glam",
}
ALLOWED_EYE_COLOR_CONTROLS = {
    "random",
    "brown_eyes",
    "hazel_eyes",
    "green_eyes",
    "blue_eyes",
    "gray_eyes",
}
ALLOWED_BREAST_SIZE_CONTROLS = {
    "random",
    "small_breasts",
    "medium_breasts",
    "big_breasts",
    "very_big_breasts",
    "extra_large_breasts",
}
ALLOWED_RACE_PRESETS = {
    "random_default_split",
    "mostly_whites",
    "mostly_blacks",
    "mostly_asian",
    "mostly_latina",
    "mostly_mixed",
    "white_american",
    "white_ukrainian",
    "white_russian",
    "white_polish",
    "white_italian",
    "white_spanish",
    "white_english",
    "black_american",
    "black_british",
    "black_nigerian",
    "latina_colombian",
    "latina_mexican",
    "latina_brazilian",
    "east_asian_chinese",
    "east_asian_japanese",
    "southeast_asian_thai",
    "southeast_asian_vietnamese",
    "southeast_asian_filipina",
    "middle_eastern",
    "south_asian",
    "other",
}
ALLOWED_PHOTO_TREATMENT_CONTROLS = {
    "random",
    "clean_commercial",
    "candid_phone_snapshot",
    "analog_35mm",
    "low_key_dramatic",
    "direct_flash_night",
    "studio_seamless",
    "cinematic_poster_realism",
    "concept_photo_editorial",
    "direct_light_editorial",
    "mirror_selfie",
    "disposable_camera",
    "documentary_still",
    "casual_indoor_selfie",
    "vintage_flash_photo",
    "advertising_poster_realism",
}
SUPPORTED_STYLE_MODES = {
    "random",
    "studio",
    "lifestyle",
    "luxury",
    "old_money",
    "romantic",
    "vacation",
    "sport",
    "fitness",
    "cosplay",
    "fantasy",
    "nightlife",
    "cultural_bookish",
    "creative_artistic",
    "urban_day",
    "coastal",
}

AGE_MAP = {
    "18": {"young_18"},
    "young 18": {"young_18"},
    "18-20": {"young_18", "young_19", "young_20"},
    "19": {"young_19"},
    "young 19": {"young_19"},
    "20": {"young_20"},
    "young 20": {"young_20"},
    "21": {"young_21"},
    "young 21": {"young_21"},
    "21-23": {"young_21", "young_22", "young_23"},
    "22": {"young_22"},
    "young 22": {"young_22"},
    "23": {"young_23"},
    "young 23": {"young_23"},
    "25-30": {"mid_20s"},
    "25": {"mid_20s"},
    "26": {"mid_20s"},
    "27": {"mid_20s"},
    "28": {"mid_20s"},
    "29": {"mid_20s"},
    "30+": {"early_30s", "late_30s"},
}

ANTI_REPEAT_PROFILES = {
    "low": {
        "use_recent_batch_rules": True,
        "use_memory_rules": False,
        "field_penalties": {
            "scene_family_id": 2,
            "setting_scene_id": 3,
            "outfit_family_id": 1,
            "pose_family_id": 1,
        },
        "unique_scene_bonus": 1,
        "unique_setting_bonus": 1,
    },
    "normal": {
        "use_recent_batch_rules": True,
        "use_memory_rules": True,
        "field_penalties": {
            "scene_family_id": 3,
            "setting_scene_id": 4,
            "outfit_family_id": 2,
            "pose_family_id": 2,
        },
        "unique_scene_bonus": 2,
        "unique_setting_bonus": 1,
    },
    "hard": {
        "use_recent_batch_rules": True,
        "use_memory_rules": True,
        "field_penalties": {
            "scene_family_id": 5,
            "setting_scene_id": 7,
            "outfit_family_id": 3,
            "pose_family_id": 3,
        },
        "unique_scene_bonus": 3,
        "unique_setting_bonus": 2,
    },
    "brutal": {
        "use_recent_batch_rules": True,
        "use_memory_rules": True,
        "field_penalties": {
            "scene_family_id": 8,
            "setting_scene_id": 10,
            "outfit_family_id": 5,
            "pose_family_id": 4,
        },
        "unique_scene_bonus": 4,
        "unique_setting_bonus": 3,
    },
}

RACE_GROUP_HINTS = {
    "white": {"white", "european", "slavic", "balkan", "nordic", "caucasian"},
    "black": {"black", "african", "afro", "ethiopian", "nigerian"},
    "asian": {"asian", "east asian", "japanese", "korean", "chinese", "thai", "vietnamese"},
    "latina": {"latina", "latino", "hispanic", "brazilian", "colombian", "mexican", "argentinian"},
    "middle_eastern": {"middle eastern", "arab", "persian", "levantine", "turkish"},
    "south_asian": {"south asian", "indian", "pakistani", "bangladeshi", "sri lankan"},
    "mixed": {"mixed", "mixed race", "biracial", "multiracial"},
}

STOP_WORDS = {
    "the",
    "and",
    "with",
    "that",
    "this",
    "from",
    "into",
    "over",
    "only",
    "read",
    "look",
    "woman",
    "female",
    "girl",
}

THEME_HINTS = [
    {
        "keywords": {"night", "nightlife", "bar", "cocktail", "wine", "club", "neon", "arcade", "karaoke", "lounge"},
        "scene_families": {"nightlife_bar", "nightlife_neon"},
        "routes": {"cinematic_night"},
        "tags": {"nightlife", "bar", "night", "neon"},
    },
    {
        "keywords": {"studio", "seamless", "backdrop", "portrait"},
        "scene_families": {"studio"},
        "routes": {"studio_portrait"},
        "tags": {"studio"},
    },
    {
        "keywords": {"beach", "coastal", "pool", "resort", "marina", "boardwalk", "sea"},
        "scene_families": {"coastal_pool", "coastal_boardwalk"},
        "routes": {"slutty_lifestyle"},
        "tags": {"coastal", "pool", "beach"},
    },
    {
        "keywords": {"book", "library", "bookish", "piano", "record", "salon", "museum"},
        "scene_families": {"culture_bookish"},
        "routes": {"luxury_interior"},
        "tags": {"bookish"},
    },
    {
        "keywords": {"garden", "courtyard", "greenhouse", "conservatory", "floral", "botanical"},
        "scene_families": {"courtyard_garden", "garden_conservatory"},
        "routes": {"casual_candid", "slutty_lifestyle"},
        "tags": {"greenhouse", "courtyard"},
    },
    {
        "keywords": {"spa", "wellness", "bath", "bathroom", "shower"},
        "scene_families": {"wellness_spa", "grooming_bath"},
        "routes": {"luxury_interior"},
        "tags": {"spa", "bathroom"},
    },
    {
        "keywords": {"luxury", "penthouse", "hotel", "suite", "heiress", "oldmoney", "old", "money"},
        "scene_families": {"residential_luxury", "hospitality_suite"},
        "routes": {"luxury_interior"},
        "tags": {"luxury", "hotelized_living"},
    },
    {
        "keywords": {"city", "urban", "rooftop", "office", "apartment"},
        "scene_families": {"urban_daylight"},
        "routes": {"casual_candid", "sports_flirt"},
        "tags": {"urban"},
    },
    {
        "keywords": {"art", "artist", "atelier", "gallery", "creative", "loft"},
        "scene_families": {"creative_gallery"},
        "routes": {"slutty_lifestyle"},
        "tags": {"art", "creative"},
    },
    {
        "keywords": {"fantasy", "cosplay", "elf", "warrior", "arcane"},
        "scene_families": {"studio", "nightlife_neon"},
        "routes": {"fantasy_cosplay"},
        "tags": {"fantasy", "studio", "neon"},
    },
    {
        "keywords": {"sport", "fitness", "athletic", "tennis", "workout", "gym"},
        "scene_families": {"urban_daylight"},
        "routes": {"sports_flirt"},
        "tags": {"sporty", "athletic", "urban"},
    },
]

SCENE_FOCUS_PREFERENCES = {
    "urban": {
        "required_scene_families": {"urban_daylight"},
        "preferred_route_ids": {"casual_candid", "sports_flirt"},
        "preferred_capture_ids": {"lifestyle_photo", "smartphone_photo", "fashion_photo"},
        "preferred_tags": {"urban"},
    },
    "luxury": {
        "required_scene_families": {"residential_luxury", "hospitality_suite", "grooming_bath"},
        "preferred_route_ids": {"luxury_interior"},
        "preferred_capture_ids": {"fashion_photo", "editorial_photo"},
        "preferred_tags": {"luxury", "hotelized_living", "bathroom"},
    },
    "bookish": {
        "required_scene_families": {"culture_bookish"},
        "preferred_route_ids": {"luxury_interior", "casual_candid"},
        "preferred_capture_ids": {"lifestyle_photo", "editorial_photo"},
        "preferred_tags": {"bookish"},
    },
    "garden": {
        "required_scene_families": {"courtyard_garden", "garden_conservatory"},
        "preferred_route_ids": {"casual_candid", "slutty_lifestyle"},
        "preferred_capture_ids": {"lifestyle_photo", "editorial_photo"},
        "preferred_tags": {"courtyard", "greenhouse", "floral"},
    },
    "coastal": {
        "required_scene_families": {"coastal_pool", "coastal_boardwalk"},
        "preferred_route_ids": {"casual_candid", "slutty_lifestyle"},
        "preferred_capture_ids": {"lifestyle_photo", "fashion_photo"},
        "preferred_tags": {"coastal", "pool", "beach"},
    },
    "nightlife": {
        "required_scene_families": {"nightlife_bar", "nightlife_neon"},
        "preferred_route_ids": {"cinematic_night"},
        "preferred_capture_ids": {"fashion_photo", "editorial_photo"},
        "preferred_tags": {"nightlife", "bar", "night", "neon"},
    },
    "studio": {
        "required_scene_families": {"studio"},
        "preferred_route_ids": {"studio_portrait"},
        "preferred_capture_ids": {"fashion_photo", "editorial_photo"},
        "preferred_tags": {"studio"},
    },
    "creative": {
        "required_scene_families": {"creative_gallery"},
        "preferred_route_ids": {"slutty_lifestyle"},
        "preferred_capture_ids": {"fashion_photo", "editorial_photo", "lifestyle_photo"},
        "preferred_tags": {"creative", "art"},
    },
    "wellness": {
        "required_scene_families": {"wellness_spa", "grooming_bath"},
        "preferred_route_ids": {"luxury_interior"},
        "preferred_capture_ids": {"fashion_photo", "editorial_photo"},
        "preferred_tags": {"spa", "bathroom", "wellness"},
    },
    "sporty": {
        "required_scene_families": {"urban_daylight"},
        "preferred_route_ids": {"sports_flirt"},
        "preferred_capture_ids": {"fashion_photo", "lifestyle_photo"},
        "preferred_tags": {"sporty", "athletic", "urban"},
    },
}

HIGH_SPICY_WOMEN_REVEALING_POSE_IDS = {
    "over_shoulder_arch_stand",
    "chair_forward_lean",
    "kneeling_arch_turn",
    "peek_a_boo_frame",
    "back_one_leg_crossed",
    "stairs_look_up_recline",
    "sofa_legs_stretched",
    "side_lie_hug_torso",
    "perch_lean_back",
    "forward_fold_cross_leg",
    "bed_back_view_turn",
    "hands_up_fixing_hair",
    "back_face_side_s_curve",
    "body_side_on_face_camera",
    "window_silhouette_arch",
    "walking_turn_look",
    "one_hand_head_one_hip",
    "arms_above_head_stand",
    "rear_edge_bed_pose",
    "mirror_hair_adjust",
    "hair_sprawl_recline",
    "table_lean_hips_back",
    "cube_side_twist_knee_hold",
    "counter_hip_lean_collar_touch",
    "bed_side_knees_angled_sweater_hold",
    "passenger_seat_twist_seatback_hold",
    "doorframe_arm_overhead_s_curve",
}
HIGH_SPICY_WOMEN_PUSHING_IT_POSE_IDS = {
    "heels_over_shoulder",
    "knees_up_arm_support",
    "legs_on_wall",
    "chair_open_angle",
    "chair_kneel_arch",
    "wall_arch_bent_knees",
    "crouch_over_shoulder",
    "squat_grounded_pose",
    "bed_kneel_sheet_grip",
}
HIGH_SPICY_WOMEN_POSE_IDS = HIGH_SPICY_WOMEN_REVEALING_POSE_IDS | HIGH_SPICY_WOMEN_PUSHING_IT_POSE_IDS
LOW_SPICY_UNSAFE_POSE_IDS = {
    "reclined_one_knee_up",
    "side_lying_lounge",
    "prone_elbows_down",
    "over_shoulder_arch_stand",
    "chair_forward_lean",
    "kneeling_arch_turn",
    "back_one_leg_crossed",
    "sofa_legs_stretched",
    "bed_back_view_turn",
    "heels_over_shoulder",
    "knees_up_arm_support",
    "body_side_on_face_camera",
    "legs_on_wall",
    "window_silhouette_arch",
    "chair_open_angle",
    "chair_kneel_arch",
    "rear_edge_bed_pose",
    "wall_arch_bent_knees",
    "crouch_over_shoulder",
    "squat_grounded_pose",
    "bed_kneel_sheet_grip",
}
HIGH_SPICY_WOMEN_REVEALING_OUTFIT_IDS = {
    "sheer_overlay_slip_dress",
    "blazer_bodysuit_set",
    "halter_cutout_jumpsuit",
    "bodycon_mesh_sleeves",
    "off_shoulder_knit_mini",
    "robe_layered_slip_set",
    "asym_cutout_column_dress",
    "structured_bustier_trousers",
    "ring_halter_trousers",
    "club_cami_wrap_skirt",
    "satin_bodysuit_wide_trousers",
    "strappy_cutout_mini_dress",
    "lined_sculptural_mini_dress",
    "lined_satin_mini_dress",
    "buttondown_shirt_dress_open_collar",
    "clean_satin_slip_dress",
    "sequin_evening_sheath_dress",
    "open_trench_mini_dress",
    "zip_front_training_set",
    "cross_strap_keyhole_active_set",
    "deep_v_jersey_jumpsuit",
    "tie_front_blouse_denim_mini",
}
HIGH_SPICY_WOMEN_PUSHING_IT_OUTFIT_IDS = {
    "corset_top_mini_skirt_set",
    "longline_bralette_sheer_shirt",
    "open_shirt_bodysuit",
    "harness_trim_blazer_set",
    "cowl_neck_micro_mini",
    "thigh_high_bodysuit_robe",
    "vinyl_trim_bodycon",
    "lace_up_cami_mini",
    "mesh_panel_bodycon",
    "sheer_buttondown_mini",
    "sheer_mesh_micro_skirt",
    "bandeau_low_rise_mini",
}
HIGH_SPICY_WOMEN_OUTFIT_IDS = HIGH_SPICY_WOMEN_REVEALING_OUTFIT_IDS | HIGH_SPICY_WOMEN_PUSHING_IT_OUTFIT_IDS


def _women_active_high_spicy_pose_ids(spicy_level: int) -> set[str]:
    if spicy_level <= 5:
        return set()
    if spicy_level == 6:
        return HIGH_SPICY_WOMEN_REVEALING_POSE_IDS
    return HIGH_SPICY_WOMEN_POSE_IDS


def _women_active_high_spicy_outfit_ids(spicy_level: int) -> set[str]:
    if spicy_level <= 5:
        return set()
    if spicy_level == 6:
        return HIGH_SPICY_WOMEN_REVEALING_OUTFIT_IDS
    return HIGH_SPICY_WOMEN_OUTFIT_IDS

OUTFIT_REVEAL_PREFERENCES = {
    "reserved": {
        "preferred_outfit_ids": {
            "cardigan_skirt",
            "cardigan_trousers",
            "blouse_trousers",
            "knit_top_trousers",
            "sweater_jeans",
            "shirt_trousers",
            "mockneck_knit_skirt",
            "silk_blouse_midi_skirt",
            "cashmere_shell_trousers",
            "structured_day_dress",
            "apron_workshop_trousers",
        },
        "preferred_material_ids": {"ribbed_knit", "tailored_woven", "soft_knit_layers", "crisp_cotton", "athletic_jersey", "washed_wool_blend", "matte_crepe"},
        "preferred_color_story_ids": {"clean_neutrals", "sport_clean_white", "sage_stone", "olive_sand", "mint_cream", "black_ivory", "terracotta_sand", "teal_cream"},
        "preferred_capture_ids": {"lifestyle_photo", "editorial_photo"},
    },
    "balanced": {
        "preferred_outfit_ids": {"cami_midi_skirt", "cardigan_skirt", "cardigan_trousers", "blouse_trousers", "shirt_trousers", "vest_trousers", "column_dress", "wrap_blouse_skirt", "halter_trousers", "knit_top_trousers", "mockneck_knit_skirt", "silk_blouse_midi_skirt", "cashmere_shell_trousers", "structured_day_dress", "sweater_jeans", "apron_workshop_trousers"},
        "preferred_material_ids": {"ribbed_knit", "satin", "tailored_woven", "crisp_cotton", "fluid_crepe", "matte_jersey", "washed_wool_blend", "matte_crepe"},
        "preferred_color_story_ids": {"clean_neutrals", "black_gold", "black_ivory", "teal_cream", "olive_sand", "sage_stone", "butter_denim", "coral_ivory", "plum_blush", "mint_cream", "lilac_smoke", "terracotta_sand", "tangerine_cream", "red_ivory", "aqua_white", "cobalt_white"},
    },
    "revealing": {
        "preferred_outfit_ids": {"mini_dress", "blazer_mini_dress", "bodysuit_trousers", "corset_trousers", "crop_top_mini_skirt", "swimsuit"} | HIGH_SPICY_WOMEN_REVEALING_OUTFIT_IDS,
        "preferred_material_ids": {"satin", "ribbed_knit", "athletic_jersey", "tailored_woven", "fluid_crepe"},
        "preferred_color_story_ids": {"black_gold", "black_ivory", "hot_pink", "lime_pop", "coral_ivory", "teal_cream", "plum_blush", "aqua_white", "cobalt_white", "red_ivory", "tangerine_cream"},
    },
    "pushing_it": {
        "preferred_outfit_ids": {"crop_top_mini_skirt", "latex_editorial", "corset_trousers", "bikini_set", "corset_top_mini_skirt_set"} | HIGH_SPICY_WOMEN_PUSHING_IT_OUTFIT_IDS,
        "preferred_material_ids": {"athletic_jersey", "vinyl_latex", "satin", "tailored_woven"},
        "preferred_color_story_ids": {"hot_pink", "lime_pop", "black_gold", "black_ivory", "coral_ivory", "cobalt_white", "aqua_white", "red_ivory", "tangerine_cream"},
    },
}

WOMEN_SCENE_FAMILY_FASHION_PREFERENCES = {
    "culture_bookish": {
        "preferred_outfit_ids": {"cardigan_skirt", "cardigan_trousers", "blouse_trousers", "knit_top_trousers", "shirt_trousers", "mockneck_knit_skirt", "silk_blouse_midi_skirt", "structured_day_dress"},
        "banned_outfit_ids": {"swimsuit", "bikini_set", "latex_editorial", "crop_top_mini_skirt", "corset_trousers", "mini_dress", "blazer_mini_dress", "bodysuit_trousers"},
        "preferred_hair_ids": {"soft_half_up", "polished_low_bun", "tucked_behind_ears_blowout", "sleek_bob"},
        "preferred_makeup_ids": {"natural_pretty", "soft_glam_clean", "clean_minimal"},
        "preferred_capture_ids": {"lifestyle_photo", "editorial_photo"},
    },
    "residential_luxury": {
        "preferred_outfit_ids": {"column_dress", "wrap_blouse_skirt", "silk_blouse_midi_skirt", "cashmere_shell_trousers", "structured_day_dress", "vest_trousers", "blouse_trousers"},
        "banned_outfit_ids": {"swimsuit", "bikini_set", "latex_editorial", "crop_top_mini_skirt"},
        "preferred_hair_ids": {"sleek_bob", "polished_low_bun", "shoulder_blowout", "tucked_behind_ears_blowout"},
        "preferred_makeup_ids": {"soft_glam_clean", "rosy_polished_minimal", "natural_pretty"},
        "preferred_capture_ids": {"editorial_photo", "fashion_photo"},
    },
    "hospitality_suite": {
        "preferred_outfit_ids": {"column_dress", "wrap_blouse_skirt", "silk_blouse_midi_skirt", "cashmere_shell_trousers", "structured_day_dress", "vest_trousers", "blouse_trousers"},
        "banned_outfit_ids": {"swimsuit", "bikini_set", "latex_editorial", "crop_top_mini_skirt"},
        "preferred_hair_ids": {"sleek_bob", "polished_low_bun", "shoulder_blowout", "tucked_behind_ears_blowout"},
        "preferred_makeup_ids": {"soft_glam_clean", "rosy_polished_minimal", "natural_pretty"},
        "preferred_capture_ids": {"editorial_photo", "fashion_photo"},
    },
    "grooming_bath": {
        "preferred_outfit_ids": {"cardigan_trousers", "blouse_trousers", "shirt_trousers", "silk_blouse_midi_skirt", "structured_day_dress"},
        "banned_outfit_ids": {"swimsuit", "bikini_set", "latex_editorial", "crop_top_mini_skirt"},
        "preferred_hair_ids": {"messy_bun", "soft_half_up", "sleek_bob", "polished_low_bun"},
        "preferred_makeup_ids": {"fresh_barely_there", "clean_minimal", "natural_pretty"},
        "preferred_capture_ids": {"lifestyle_photo", "editorial_photo"},
    },
    "courtyard_garden": {
        "preferred_outfit_ids": {"wrap_blouse_skirt", "silk_blouse_midi_skirt", "structured_day_dress", "mockneck_knit_skirt", "cardigan_skirt"},
        "banned_outfit_ids": {"swimsuit", "bikini_set", "latex_editorial"},
        "preferred_hair_ids": {"soft_waves", "side_braid", "long_straight", "soft_half_up"},
        "preferred_makeup_ids": {"natural_pretty", "soft_glam_clean"},
        "preferred_capture_ids": {"lifestyle_photo", "editorial_photo"},
    },
    "garden_conservatory": {
        "preferred_outfit_ids": {"wrap_blouse_skirt", "silk_blouse_midi_skirt", "structured_day_dress", "mockneck_knit_skirt", "cardigan_skirt"},
        "banned_outfit_ids": {"swimsuit", "bikini_set", "latex_editorial"},
        "preferred_hair_ids": {"soft_waves", "side_braid", "long_straight", "soft_half_up"},
        "preferred_makeup_ids": {"natural_pretty", "soft_glam_clean"},
        "preferred_capture_ids": {"lifestyle_photo", "editorial_photo"},
    },
    "coastal_pool": {
        "preferred_outfit_ids": {"swimsuit", "bikini_set", "mini_dress", "wrap_blouse_skirt"},
        "preferred_hair_ids": {"soft_waves", "high_ponytail", "side_braid", "long_straight"},
        "preferred_makeup_ids": {"natural_pretty", "soft_glam_clean"},
        "preferred_capture_ids": {"lifestyle_photo", "fashion_photo"},
    },
    "coastal_boardwalk": {
        "preferred_outfit_ids": {"mini_dress", "wrap_blouse_skirt", "silk_blouse_midi_skirt", "cardigan_skirt", "blouse_trousers"},
        "preferred_hair_ids": {"soft_waves", "high_ponytail", "side_braid", "long_straight"},
        "preferred_makeup_ids": {"natural_pretty", "soft_glam_clean"},
        "preferred_capture_ids": {"lifestyle_photo", "fashion_photo"},
    },
    "nightlife_bar": {
        "banned_outfit_ids": {"cardigan_trousers", "blouse_trousers", "shirt_trousers", "structured_day_dress", "silk_blouse_midi_skirt", "knit_top_trousers", "cashmere_shell_trousers", "cardigan_skirt", "sweater_jeans"},
        "preferred_outfit_ids": {"mini_dress", "blazer_mini_dress", "bodysuit_trousers", "corset_trousers"},
        "preferred_hair_ids": {"soft_waves", "high_ponytail", "long_straight", "sleek_bob"},
        "preferred_makeup_ids": {"night_out_glam", "glossy_soft_glam"},
        "preferred_capture_ids": {"fashion_photo", "editorial_photo"},
    },
    "nightlife_neon": {
        "banned_outfit_ids": {"cardigan_trousers", "blouse_trousers", "shirt_trousers", "structured_day_dress", "silk_blouse_midi_skirt", "knit_top_trousers", "cashmere_shell_trousers", "cardigan_skirt", "sweater_jeans"},
        "preferred_outfit_ids": {"mini_dress", "blazer_mini_dress", "bodysuit_trousers", "latex_editorial"},
        "preferred_hair_ids": {"soft_waves", "high_ponytail", "long_straight", "sleek_bob"},
        "preferred_makeup_ids": {"night_out_glam", "glossy_soft_glam"},
        "preferred_capture_ids": {"fashion_photo", "editorial_photo"},
    },
    "studio": {
        "preferred_outfit_ids": {"mini_dress", "blazer_mini_dress", "column_dress", "silk_blouse_midi_skirt"},
        "preferred_hair_ids": {"sleek_bob", "blunt_bob", "polished_low_bun", "soft_half_up"},
        "preferred_makeup_ids": {"soft_glam_clean", "rosy_polished_minimal", "natural_pretty"},
        "preferred_capture_ids": {"fashion_photo", "editorial_photo", "studio_portrait"},
    },
    "creative_gallery": {
        "preferred_outfit_ids": {"blazer_mini_dress", "cami_midi_skirt", "wrap_blouse_skirt", "latex_editorial", "silk_blouse_midi_skirt"},
        "preferred_hair_ids": {"soft_waves", "sleek_bob", "blunt_bob", "soft_half_up"},
        "preferred_makeup_ids": {"glossy_soft_glam", "soft_glam_clean", "natural_pretty"},
        "preferred_capture_ids": {"editorial_photo", "fashion_photo"},
    },
    "urban_daylight": {
        "preferred_outfit_ids": {"cardigan_trousers", "blouse_trousers", "shirt_trousers", "mini_dress", "structured_day_dress", "wrap_blouse_skirt"},
        "banned_outfit_ids": {"swimsuit", "bikini_set", "latex_editorial", "corset_trousers"},
        "preferred_hair_ids": {"high_ponytail", "shoulder_blowout", "soft_half_up", "tucked_behind_ears_blowout"},
        "preferred_makeup_ids": {"natural_pretty", "groomed_daylight_soft", "clean_minimal"},
        "preferred_capture_ids": {"lifestyle_photo", "smartphone_photo", "fashion_photo"},
    },
    "wellness_spa": {
        "preferred_outfit_ids": {"cardigan_trousers", "blouse_trousers", "shirt_trousers", "structured_day_dress", "silk_blouse_midi_skirt"},
        "banned_outfit_ids": {"swimsuit", "bikini_set", "latex_editorial", "crop_top_mini_skirt", "mini_dress", "blazer_mini_dress", "bodysuit_trousers", "corset_trousers"},
        "preferred_hair_ids": {"sleek_bob", "messy_bun", "soft_half_up", "polished_low_bun"},
        "preferred_makeup_ids": {"fresh_barely_there", "clean_minimal", "natural_pretty"},
        "preferred_capture_ids": {"lifestyle_photo", "editorial_photo"},
    },
}

WOMEN_SCENE_FAMILY_OUTFIT_REVEAL = {
    "culture_bookish": "reserved",
    "residential_luxury": "balanced",
    "hospitality_suite": "balanced",
    "grooming_bath": "reserved",
    "courtyard_garden": "balanced",
    "garden_conservatory": "balanced",
    "coastal_pool": "revealing",
    "coastal_boardwalk": "balanced",
    "nightlife_bar": "revealing",
    "nightlife_neon": "revealing",
    "studio": "balanced",
    "creative_gallery": "revealing",
    "urban_daylight": "reserved",
    "wellness_spa": "reserved",
}

WOMEN_BANNED_HAIR_IDS = {
    "male_clean_side_part",
    "male_textured_crop",
    "male_medium_pushback",
    "male_soft_quiff",
    "male_wavy_brushback",
}

WOMEN_SCENE_FAMILY_FASHION_PREFERENCES = {
    "culture_bookish": {
        "preferred_outfit_ids": {"cardigan_skirt", "cardigan_trousers", "blouse_trousers", "knit_top_trousers", "shirt_trousers", "mockneck_knit_skirt", "silk_blouse_midi_skirt", "structured_day_dress"},
        "banned_outfit_ids": {"swimsuit", "bikini_set", "latex_editorial", "crop_top_mini_skirt", "corset_trousers", "mini_dress", "blazer_mini_dress", "bodysuit_trousers"},
        "preferred_hair_ids": {"soft_half_up", "polished_low_bun", "tucked_behind_ears_blowout", "sleek_bob"},
        "preferred_makeup_ids": {"natural_pretty", "soft_glam_clean", "clean_minimal"},
        "preferred_capture_ids": {"lifestyle_photo", "editorial_photo"},
    },
    "residential_luxury": {
        "preferred_outfit_ids": {"column_dress", "wrap_blouse_skirt", "silk_blouse_midi_skirt", "cashmere_shell_trousers", "structured_day_dress", "vest_trousers", "blouse_trousers"},
        "banned_outfit_ids": {"swimsuit", "bikini_set", "latex_editorial", "crop_top_mini_skirt"},
        "preferred_hair_ids": {"sleek_bob", "polished_low_bun", "shoulder_blowout", "tucked_behind_ears_blowout"},
        "preferred_makeup_ids": {"soft_glam_clean", "rosy_polished_minimal", "natural_pretty"},
        "preferred_capture_ids": {"editorial_photo", "fashion_photo"},
    },
    "hospitality_suite": {
        "preferred_outfit_ids": {"column_dress", "wrap_blouse_skirt", "silk_blouse_midi_skirt", "cashmere_shell_trousers", "structured_day_dress", "vest_trousers", "blouse_trousers"},
        "banned_outfit_ids": {"swimsuit", "bikini_set", "latex_editorial", "crop_top_mini_skirt"},
        "preferred_hair_ids": {"sleek_bob", "polished_low_bun", "shoulder_blowout", "tucked_behind_ears_blowout"},
        "preferred_makeup_ids": {"soft_glam_clean", "rosy_polished_minimal", "natural_pretty"},
        "preferred_capture_ids": {"editorial_photo", "fashion_photo"},
    },
    "grooming_bath": {
        "preferred_outfit_ids": {"cardigan_trousers", "blouse_trousers", "shirt_trousers", "silk_blouse_midi_skirt", "structured_day_dress"},
        "banned_outfit_ids": {"swimsuit", "bikini_set", "latex_editorial", "crop_top_mini_skirt"},
        "preferred_hair_ids": {"messy_bun", "soft_half_up", "sleek_bob", "polished_low_bun"},
        "preferred_makeup_ids": {"fresh_barely_there", "clean_minimal", "natural_pretty"},
        "preferred_capture_ids": {"lifestyle_photo", "editorial_photo"},
    },
    "courtyard_garden": {
        "preferred_outfit_ids": {"wrap_blouse_skirt", "silk_blouse_midi_skirt", "structured_day_dress", "mockneck_knit_skirt", "cardigan_skirt"},
        "banned_outfit_ids": {"swimsuit", "bikini_set", "latex_editorial"},
        "preferred_hair_ids": {"soft_waves", "side_braid", "long_straight", "soft_half_up"},
        "preferred_makeup_ids": {"natural_pretty", "soft_glam_clean"},
        "preferred_capture_ids": {"lifestyle_photo", "editorial_photo"},
    },
    "garden_conservatory": {
        "preferred_outfit_ids": {"wrap_blouse_skirt", "silk_blouse_midi_skirt", "structured_day_dress", "mockneck_knit_skirt", "cardigan_skirt"},
        "banned_outfit_ids": {"swimsuit", "bikini_set", "latex_editorial"},
        "preferred_hair_ids": {"soft_waves", "side_braid", "long_straight", "soft_half_up"},
        "preferred_makeup_ids": {"natural_pretty", "soft_glam_clean"},
        "preferred_capture_ids": {"lifestyle_photo", "editorial_photo"},
    },
    "coastal_pool": {
        "preferred_outfit_ids": {"swimsuit", "bikini_set", "mini_dress", "wrap_blouse_skirt"},
        "preferred_hair_ids": {"soft_waves", "high_ponytail", "side_braid", "long_straight"},
        "preferred_makeup_ids": {"natural_pretty", "soft_glam_clean"},
        "preferred_capture_ids": {"lifestyle_photo", "fashion_photo"},
    },
    "coastal_boardwalk": {
        "preferred_outfit_ids": {"mini_dress", "wrap_blouse_skirt", "silk_blouse_midi_skirt", "cardigan_skirt", "blouse_trousers"},
        "preferred_hair_ids": {"soft_waves", "high_ponytail", "side_braid", "long_straight"},
        "preferred_makeup_ids": {"natural_pretty", "soft_glam_clean"},
        "preferred_capture_ids": {"lifestyle_photo", "fashion_photo"},
    },
    "nightlife_bar": {
        "banned_outfit_ids": {"cardigan_trousers", "blouse_trousers", "shirt_trousers", "structured_day_dress", "silk_blouse_midi_skirt", "knit_top_trousers", "cashmere_shell_trousers", "cardigan_skirt", "sweater_jeans"},
        "preferred_outfit_ids": {"mini_dress", "blazer_mini_dress", "bodysuit_trousers", "corset_trousers"},
        "preferred_hair_ids": {"soft_waves", "high_ponytail", "long_straight", "sleek_bob"},
        "preferred_makeup_ids": {"night_out_glam", "glossy_soft_glam"},
        "preferred_capture_ids": {"fashion_photo", "editorial_photo"},
    },
    "nightlife_neon": {
        "banned_outfit_ids": {"cardigan_trousers", "blouse_trousers", "shirt_trousers", "structured_day_dress", "silk_blouse_midi_skirt", "knit_top_trousers", "cashmere_shell_trousers", "cardigan_skirt", "sweater_jeans"},
        "preferred_outfit_ids": {"mini_dress", "blazer_mini_dress", "bodysuit_trousers", "latex_editorial"},
        "preferred_hair_ids": {"soft_waves", "high_ponytail", "long_straight", "sleek_bob"},
        "preferred_makeup_ids": {"night_out_glam", "glossy_soft_glam"},
        "preferred_capture_ids": {"fashion_photo", "editorial_photo"},
    },
    "studio": {
        "preferred_outfit_ids": {"mini_dress", "blazer_mini_dress", "column_dress", "silk_blouse_midi_skirt"},
        "preferred_hair_ids": {"sleek_bob", "blunt_bob", "polished_low_bun", "soft_half_up"},
        "preferred_makeup_ids": {"soft_glam_clean", "rosy_polished_minimal", "natural_pretty"},
        "preferred_capture_ids": {"fashion_photo", "editorial_photo", "studio_portrait"},
    },
    "creative_gallery": {
        "preferred_outfit_ids": {"blazer_mini_dress", "cami_midi_skirt", "wrap_blouse_skirt", "latex_editorial", "silk_blouse_midi_skirt"},
        "preferred_hair_ids": {"soft_waves", "sleek_bob", "blunt_bob", "soft_half_up"},
        "preferred_makeup_ids": {"glossy_soft_glam", "soft_glam_clean", "natural_pretty"},
        "preferred_capture_ids": {"editorial_photo", "fashion_photo"},
    },
    "urban_daylight": {
        "preferred_outfit_ids": {"cardigan_trousers", "blouse_trousers", "shirt_trousers", "mini_dress", "structured_day_dress", "wrap_blouse_skirt"},
        "banned_outfit_ids": {"swimsuit", "bikini_set", "latex_editorial", "corset_trousers"},
        "preferred_hair_ids": {"high_ponytail", "shoulder_blowout", "soft_half_up", "tucked_behind_ears_blowout"},
        "preferred_makeup_ids": {"natural_pretty", "groomed_daylight_soft", "clean_minimal"},
        "preferred_capture_ids": {"lifestyle_photo", "smartphone_photo", "fashion_photo"},
    },
    "wellness_spa": {
        "preferred_outfit_ids": {"cardigan_trousers", "blouse_trousers", "shirt_trousers", "structured_day_dress", "silk_blouse_midi_skirt"},
        "banned_outfit_ids": {"swimsuit", "bikini_set", "latex_editorial", "crop_top_mini_skirt", "mini_dress", "blazer_mini_dress", "bodysuit_trousers", "corset_trousers"},
        "preferred_hair_ids": {"sleek_bob", "messy_bun", "soft_half_up", "polished_low_bun"},
        "preferred_makeup_ids": {"fresh_barely_there", "clean_minimal", "natural_pretty"},
        "preferred_capture_ids": {"lifestyle_photo", "editorial_photo"},
    },
}

WOMEN_SCENE_FAMILY_OUTFIT_REVEAL = {
    "culture_bookish": "reserved",
    "residential_luxury": "balanced",
    "hospitality_suite": "balanced",
    "grooming_bath": "reserved",
    "courtyard_garden": "balanced",
    "garden_conservatory": "balanced",
    "coastal_pool": "revealing",
    "coastal_boardwalk": "balanced",
    "nightlife_bar": "revealing",
    "nightlife_neon": "revealing",
    "studio": "balanced",
    "creative_gallery": "revealing",
    "urban_daylight": "reserved",
    "wellness_spa": "reserved",
}

HAIR_LENGTH_PREFERENCES = {
    "short": {"sleek_bob", "natural_curls", "blunt_bob"},
    "medium": {"shoulder_blowout", "messy_bun", "polished_low_bun", "tucked_behind_ears_blowout"},
    "long": {"soft_waves", "high_ponytail", "side_braid", "long_straight", "soft_half_up"},
}

HAIR_COLOR_PREFERENCES = {
    "black": {"black_natural"},
    "dark_brown": {"dark_brown_natural"},
    "brown": {"medium_brown_natural", "dark_brown_natural"},
    "light_brown": {"light_brown_natural", "medium_brown_natural"},
    "blonde": {"blonde_natural"},
    "dark_blonde": {"dark_blonde_natural"},
    "red_ginger": {"copper_dyed", "auburn_natural"},
    "auburn": {"auburn_natural", "burgundy_dyed"},
    "gray_silver": {"silver_dyed"},
}

DYED_NATURAL_HAIR_COLOR_IDS = {"copper_dyed", "burgundy_dyed", "silver_dyed"}

SAME_PERSON_RACE_GROUPS = {
    "mostly_whites": "white",
    "mostly_blacks": "black",
    "mostly_asian": "asian",
    "mostly_latina": "latina",
}
SAME_PERSON_ETHNICITY_IDS = {
    "white_american",
    "white_ukrainian",
    "white_russian",
    "white_polish",
    "white_italian",
    "white_spanish",
    "white_english",
    "black_american",
    "black_british",
    "black_nigerian",
    "latina_colombian",
    "latina_mexican",
    "latina_brazilian",
    "east_asian_chinese",
    "east_asian_japanese",
    "southeast_asian_thai",
    "southeast_asian_vietnamese",
    "southeast_asian_filipina",
    "middle_eastern",
    "south_asian",
}

SAME_PERSON_BODY_GROUPS = {
    "slim_lean": {"lean"},
    "toned": {"toned"},
    "athletic": {"athletic"},
    "curvy": {"curvy"},
}


def _parse_bool(value: Any) -> bool:
    return form_normalizer._parse_bool(value)


def _normalize_choice(value: Any, allowed: set[str], default: str) -> str:
    return form_normalizer._normalize_choice(value, allowed, default)


def _safe_int(value: Any, default: int) -> int:
    return form_normalizer._safe_int(value, default)


def _clean_text(value: Any, max_length: int = 180) -> str:
    return form_normalizer._clean_text(value, max_length=max_length)


def _tokenize_text(value: str) -> list[str]:
    return form_normalizer._tokenize_text(value)


def _female_appearance_mode(form_state: dict[str, Any]) -> str:
    return form_normalizer._female_appearance_mode(form_state)


def _male_appearance_mode(form_state: dict[str, Any]) -> str:
    return form_normalizer._male_appearance_mode(form_state)


def _female_appearance_prompt(form_state: dict[str, Any]) -> str:
    return form_normalizer._female_appearance_prompt(form_state)


def _male_appearance_prompt(form_state: dict[str, Any]) -> str:
    return form_normalizer._male_appearance_prompt(form_state)


def _male_outfit_control_value(value: Any) -> str:
    return form_normalizer._male_outfit_control_value(value)


def _female_custom_appearance_active(form_state: dict[str, Any]) -> bool:
    return form_normalizer._female_custom_appearance_active(form_state)


def _male_custom_appearance_active(form_state: dict[str, Any]) -> bool:
    return form_normalizer._male_custom_appearance_active(form_state)


def _merged_form_state(incoming: dict[str, Any] | None) -> dict[str, Any]:
    return form_normalizer._merged_form_state(incoming)


def merged_form_state(incoming: dict[str, Any] | None) -> dict[str, Any]:
    return _merged_form_state(incoming)


def _effective_spicy_level(form_state: dict[str, Any]) -> int:
    return form_runtime_controls._effective_spicy_level(form_state)


def _location_strategy_flags(form_state: dict[str, Any]) -> str:
    return form_runtime_controls._location_strategy_flags(form_state)


def _anti_repeat_profile(form_state: dict[str, Any]) -> dict[str, Any]:
    return form_runtime_controls._anti_repeat_profile(form_state)


def _resolve_runtime_controls(form_state: dict[str, Any]) -> tuple[int, bool, bool, str, str]:
    return form_runtime_controls._resolve_runtime_controls(form_state)


def resolve_runtime_controls(form_state: dict[str, Any]) -> tuple[int, bool, bool, str, str]:
    return _resolve_runtime_controls(form_state)


def _normalize_age_filter(value: str) -> set[str] | None:
    return scoring._normalize_age_filter(value)


def _custom_race_group(custom_race: str) -> str | None:
    return scoring._custom_race_group(custom_race)


def _custom_race_preferences(custom_race: str) -> tuple[str | None, set[str]]:
    return scoring._custom_race_preferences(custom_race)


def _custom_race_candidate_score(candidate: dict[str, Any], custom_race: str) -> int:
    return scoring._custom_race_candidate_score(candidate, custom_race)


def _couples_different_persons_identity_constraints(form_state: dict[str, Any]) -> dict[str, set[str]]:
    return scoring._couples_different_persons_identity_constraints(form_state)


def _male_age_matches_request(age_text: str, requested: str) -> bool:
    return scoring._male_age_matches_request(age_text, requested)


def _custom_race_matches_identity_text(custom_race: str, identity: dict[str, Any]) -> bool:
    return scoring._custom_race_matches_identity_text(custom_race, identity)


def _male_race_matches_request(male_identity: dict[str, Any], race_preset: str, custom_race: str = "") -> bool:
    return scoring._male_race_matches_request(male_identity, race_preset, custom_race)


def _explicit_male_identity_constraints_active(form_state: dict[str, Any]) -> bool:
    return scoring._explicit_male_identity_constraints_active(form_state)


def _couples_male_identity_score(
    batch: list[dict[str, Any]],
    form_state: dict[str, Any],
    style_mode: str,
    seed: int,
) -> tuple[int, bool]:
    return scoring._couples_male_identity_score(batch, form_state, style_mode, seed)

    male_age_value = str(form_state.get("maleAge", "Random") or "Random")
    male_race_preset = str(form_state.get("maleRacePreset", "random_default_split") or "random_default_split")
    male_custom_race = str(form_state.get("maleCustomRace", "") or "")
    male_identities = preview_male_identities("couples", batch, form_state, style_mode, seed)
    score = 0
    hard_fail = False

    if male_age_value.strip().lower() not in {"", "random"}:
        age_matches = sum(1 for male_identity in male_identities if _male_age_matches_request(str(male_identity.get("age", "")), male_age_value))
        age_misses = len(male_identities) - age_matches
        score += age_matches * 12 - age_misses * 24
        if age_misses:
            hard_fail = True

    if male_race_preset != "random_default_split" or male_custom_race:
        race_matches = sum(1 for male_identity in male_identities if _male_race_matches_request(male_identity, male_race_preset, male_custom_race))
        race_misses = len(male_identities) - race_matches
        score += race_matches * 12 - race_misses * 24
        if race_misses:
            hard_fail = True

    return score, hard_fail


def _race_score(batch: list[dict[str, Any]], race_preset: str, custom_race: str = "") -> int:
    return scoring._race_score(batch, race_preset, custom_race)
    if race_preset == "other":
        return sum(_custom_race_candidate_score(candidate, custom_race) for candidate in batch)
    if race_preset in SAME_PERSON_ETHNICITY_IDS:
        return sum(16 if candidate["ethnicity_id"] == race_preset else -6 for candidate in batch)
    groups = [candidate["ethnicity_group"] for candidate in batch]
    counts = Counter(groups)
    size = len(batch)
    if race_preset == "mostly_mixed":
        return min(50, len(counts) * 12)
    target_map = {
        "mostly_whites": "white",
        "mostly_blacks": "black",
        "mostly_asian": "asian",
        "mostly_latina": "latina",
    }
    target = target_map.get(race_preset)
    if not target:
        return 0
    return counts.get(target, 0) * 12 - (size - counts.get(target, 0)) * 3


def _body_score(batch: list[dict[str, Any]], preset: str) -> int:
    return scoring._body_score(batch, preset)
    groups = [candidate["body_group"] for candidate in batch]
    counts = Counter(groups)
    if preset == "slim_lean":
        return counts.get("lean", 0) * 10
    if preset == "toned":
        return counts.get("toned", 0) * 10
    if preset == "athletic":
        return counts.get("athletic", 0) * 10
    if preset == "curvy":
        return counts.get("curvy", 0) * 10
    if preset == "mixed_curvy_accent":
        return counts.get("curvy", 0) * 8 + (len(counts) > 1) * 10
    if preset == "mixed_athletic_accent":
        return counts.get("athletic", 0) * 8 + (len(counts) > 1) * 10
    return 0


def _style_score(candidate: dict[str, Any], style_mode: str) -> int:
    return scoring._style_score(candidate, style_mode)
    scene = candidate["scene_family_id"]
    route = candidate["route"]
    capture = candidate["capture_style_id"]
    tags = set(candidate.get("tags", []))
    rules: dict[str, tuple[set[str], set[str], set[str]]] = {
        "studio": ({"studio"}, {"studio_portrait"}, {"editorial_photo", "fashion_photo"}),
        "lifestyle": ({"urban_daylight", "culture_bookish", "garden_conservatory"}, {"casual_candid", "amateur_phone"}, {"lifestyle_photo", "smartphone_photo"}),
        "luxury": ({"residential_luxury", "hospitality_suite", "grooming_bath"}, {"luxury_interior"}, {"editorial_photo", "fashion_photo"}),
        "old_money": ({"residential_luxury", "culture_bookish", "garden_conservatory"}, {"luxury_interior", "casual_candid"}, {"editorial_photo", "lifestyle_photo"}),
        "romantic": ({"courtyard_garden", "garden_conservatory", "coastal_pool"}, {"casual_candid"}, {"lifestyle_photo", "editorial_photo"}),
        "vacation": ({"coastal_boardwalk", "coastal_pool", "hospitality_suite", "wellness_spa"}, {"casual_candid", "luxury_interior", "slutty_lifestyle"}, {"lifestyle_photo", "fashion_photo"}),
        "sport": ({"urban_daylight"}, {"sports_flirt"}, {"fashion_photo", "lifestyle_photo"}),
        "fitness": ({"urban_daylight", "wellness_spa"}, {"sports_flirt", "luxury_interior"}, {"fashion_photo", "lifestyle_photo"}),
        "cosplay": ({"studio"}, {"fantasy_cosplay"}, {"editorial_photo", "fashion_photo"}),
        "fantasy": ({"studio"}, {"fantasy_cosplay"}, {"editorial_photo", "fashion_photo"}),
        "nightlife": ({"nightlife_bar", "nightlife_neon"}, {"cinematic_night"}, {"editorial_photo", "fashion_photo"}),
        "cultural_bookish": ({"culture_bookish"}, {"casual_candid", "luxury_interior"}, {"editorial_photo", "lifestyle_photo"}),
        "creative_artistic": ({"creative_gallery"}, {"casual_candid"}, {"editorial_photo", "fashion_photo"}),
        "urban_day": ({"urban_daylight"}, {"casual_candid", "amateur_phone"}, {"lifestyle_photo", "smartphone_photo"}),
        "coastal": ({"coastal_boardwalk", "coastal_pool"}, {"slutty_lifestyle", "casual_candid"}, {"lifestyle_photo", "fashion_photo"}),
    }
    scenes, routes, captures = rules.get(style_mode, (set(), set(), set()))
    score = 0
    if scene in scenes:
        score += 10
    if route in routes:
        score += 8
    if capture in captures:
        score += 6
    if style_mode in {"sport", "fitness"} and {"sporty", "athletic"} & tags:
        score += 8
    if style_mode == "sport":
        score += 12 if candidate["outfit_family_id"] == "crop_top_mini_skirt" else -18
        score += 12 if candidate["material_id"] == "athletic_jersey" else -10
        score += 10 if candidate["scene_family_id"] == "urban_daylight" else -16
        score += 8 if candidate["route"] == "sports_flirt" else -14
        score += 2 if candidate["hair_structure_id"] == "high_ponytail" else 0
    if style_mode == "fitness":
        fitness_safe_outfits = {"polo_pleated_skirt", "workout_top_leggings", "zip_jacket_leggings", "training_jacket_trousers"}
        fitness_safe_colors = {"sport_clean_white", "navy_cream", "earthy_soft", "powder_blue", "clean_neutrals"}
        score += 14 if candidate["outfit_family_id"] in fitness_safe_outfits else -20
        score -= 26 if candidate["outfit_family_id"] == "crop_top_mini_skirt" else 0
        score += 12 if candidate["material_id"] == "athletic_jersey" else -8
        score += 12 if candidate["scene_family_id"] in {"urban_daylight", "wellness_spa"} else -16
        score += 10 if candidate["route"] in {"sports_flirt", "luxury_interior"} else -14
        score += 2 if candidate["hair_structure_id"] == "high_ponytail" else 0
        score += 8 if candidate.get("color_story_id") in fitness_safe_colors else -6
        score += 6 if candidate["scene_family_id"] == "wellness_spa" else 0
        score += 4 if {"wellness", "sporty"} & tags else 0
    if style_mode in {"old_money", "luxury"} and "luxury" in tags:
        score += 6
    if style_mode == "nightlife" and candidate.get("material_id") == "vinyl_latex":
        score -= 28
    if style_mode == "nightlife":
        if candidate.get("outfit_family_id") == "mini_dress":
            score -= 4
        if candidate.get("outfit_family_id") in {"cami_midi_skirt", "wrap_blouse_skirt", "column_dress", "halter_trousers", "silk_blouse_midi_skirt"}:
            score += 6
    if style_mode == "lifestyle":
        if candidate.get("outfit_family_id") == "mini_dress":
            score -= 8
        if candidate.get("outfit_family_id") in {"blazer_mini_dress", "bodysuit_trousers", "corset_trousers"}:
            score -= 12
        if candidate.get("color_story_id") in {"black_gold", "oxblood_noir", "emerald_noir", "hot_pink"}:
            score -= 10
    if style_mode == "random":
        if candidate.get("outfit_family_id") == "mini_dress":
            score -= 8
        if candidate.get("outfit_family_id") in {"column_dress", "wrap_blouse_skirt", "vest_trousers", "blouse_trousers", "shirt_trousers", "cami_midi_skirt", "silk_blouse_midi_skirt", "mockneck_knit_skirt", "cashmere_shell_trousers", "structured_day_dress"}:
            score += 6
        if candidate.get("color_story_id") == "clean_neutrals":
            score -= 4
    if style_mode == "romantic":
        if candidate.get("scene_family_id") == "coastal_pool":
            score -= 10
        if candidate.get("outfit_family_id") in {"cami_midi_skirt", "wrap_blouse_skirt", "column_dress", "halter_trousers", "silk_blouse_midi_skirt", "structured_day_dress", "mockneck_knit_skirt"}:
            score += 8
        if candidate.get("outfit_family_id") in {"corset_trousers", "bodysuit_trousers", "blazer_mini_dress", "cardigan_skirt"}:
            score -= 10
        if candidate.get("outfit_family_id") in {"blouse_trousers", "knit_top_trousers", "cardigan_trousers", "sweater_jeans"}:
            score -= 6
    if style_mode == "luxury":
        if candidate.get("outfit_family_id") == "mini_dress":
            score -= 12
        if candidate.get("outfit_family_id") in {"column_dress", "wrap_blouse_skirt", "vest_trousers", "blouse_trousers", "cami_midi_skirt", "halter_trousers", "cashmere_shell_trousers", "structured_day_dress", "silk_blouse_midi_skirt"}:
            score += 8
        if candidate.get("color_story_id") == "clean_neutrals":
            score -= 6
    if style_mode == "creative_artistic":
        if candidate.get("outfit_family_id") in {"vest_trousers", "column_dress", "wrap_blouse_skirt", "halter_trousers", "apron_workshop_trousers", "silk_blouse_midi_skirt"}:
            score += 10
        if candidate.get("color_story_id") in {"slate_blue_ink", "rosewood_smoke", "black_gold", "emerald_noir"}:
            score += 6
        if candidate.get("outfit_family_id") in {"polo_pleated_skirt", "workout_top_leggings", "zip_jacket_leggings", "training_jacket_trousers"}:
            score -= 18
        if candidate.get("outfit_family_id") == "mini_dress":
            score -= 8
    return score


def _photo_treatment_lookup() -> dict[str, dict[str, Any]]:
    from .services.photo_treatment_lookup import _photo_treatment_lookup as photo_treatment_lookup

    return photo_treatment_lookup()


def _style_debug_signals(candidate: dict[str, Any], style_mode: str, scene_focus: str) -> dict[str, list[str]]:
    from .services.debug_summary import _style_debug_signals as debug_summary_style_debug_signals

    return debug_summary_style_debug_signals(candidate, style_mode, scene_focus)


def _treatment_debug_signals(candidate: dict[str, Any], style_mode: str) -> dict[str, list[str]]:
    from .services.debug_summary import _treatment_debug_signals as debug_summary_treatment_debug_signals

    return debug_summary_treatment_debug_signals(candidate, style_mode)


def _photo_treatment_candidate_score(candidate: dict[str, Any], style_mode: str, mode: str = "women") -> int:
    return scoring._photo_treatment_candidate_score(candidate, style_mode, mode)
    profile = _photo_treatment_lookup().get(treatment_id)
    if not profile:
        return 0
    score = 0
    harder_lanes = {"concept_photo_editorial", "direct_light_editorial"}
    casual_stylized_lanes = {
        "mirror_selfie",
        "disposable_camera",
        "documentary_still",
        "casual_indoor_selfie",
        "vintage_flash_photo",
        "advertising_poster_realism",
    }
    scene_family = candidate.get("scene_family_id", "")
    capture_id = candidate.get("capture_style_id", "")
    lighting_id = candidate.get("lighting_family_id", "")
    time_id = candidate.get("time_of_day_id", "")
    allowed_scenes = {str(value) for value in profile.get("allowed_scene_families", [])}
    banned_scenes = {str(value) for value in profile.get("banned_scene_families", [])}
    allowed_styles = {str(value) for value in profile.get("allowed_style_modes", [])}
    banned_styles = {str(value) for value in profile.get("banned_style_modes", [])}
    preferred_scenes = {str(value) for value in profile.get("preferred_scene_families", [])}
    preferred_styles = {str(value) for value in profile.get("preferred_style_modes", [])}
    preferred_captures = {str(value) for value in profile.get("preferred_capture_ids", [])}
    preferred_lighting = {str(value) for value in profile.get("preferred_lighting_ids", [])}
    preferred_times = {str(value) for value in profile.get("preferred_time_ids", [])}

    if allowed_scenes and scene_family not in allowed_scenes:
        score -= 24
    if scene_family in banned_scenes:
        score -= 28
    if allowed_styles and style_mode not in allowed_styles and style_mode != "random":
        score -= 18
    if style_mode in banned_styles:
        score -= 24
    if scene_family in preferred_scenes:
        score += 12
    if style_mode in preferred_styles:
        score += 9
    if capture_id in preferred_captures:
        score += 8
    if lighting_id in preferred_lighting:
        score += 8
    if time_id in preferred_times:
        score += 6

    category = candidate.get("photo_treatment_category", "")
    if style_mode == "random":
        score += 3 if category == "stylized" else 2
        if treatment_id in harder_lanes:
            score += 8
        if treatment_id in casual_stylized_lanes:
            score += 6
        if treatment_id == "clean_commercial":
            score += 8
        if mode == "women":
            if treatment_id in {"disposable_camera", "documentary_still", "mirror_selfie", "candid_phone_snapshot", "vintage_flash_photo", "advertising_poster_realism"}:
                score += 6
            if treatment_id == "clean_commercial":
                score += 10
        if mode == "couples" and treatment_id == "clean_commercial":
            score += 10
    elif style_mode in {"nightlife", "studio", "creative_artistic"}:
        score += 8 if category == "stylized" else -3
        if treatment_id in harder_lanes:
            score += 14
        if style_mode == "nightlife" and treatment_id == "vintage_flash_photo":
            score += 10
        if style_mode == "nightlife" and treatment_id in {"direct_flash_night", "low_key_dramatic", "cinematic_poster_realism"}:
            score += 8
        if style_mode == "nightlife" and treatment_id == "clean_commercial":
            score -= 10
        if mode == "women" and style_mode == "nightlife":
            if treatment_id in {"vintage_flash_photo", "direct_flash_night", "low_key_dramatic", "cinematic_poster_realism", "disposable_camera", "concept_photo_editorial"}:
                score += 8
            if treatment_id == "clean_commercial":
                score -= 10
        if style_mode == "studio" and treatment_id == "advertising_poster_realism":
            score += 10
        if style_mode == "creative_artistic" and treatment_id in {"vintage_flash_photo", "advertising_poster_realism"}:
            score += 8
        if mode == "women" and style_mode == "creative_artistic":
            if treatment_id in {"concept_photo_editorial", "direct_light_editorial", "advertising_poster_realism", "vintage_flash_photo", "documentary_still"}:
                score += 8
            if treatment_id == "clean_commercial":
                score -= 10
    elif style_mode in {"luxury", "romantic"}:
        score += 9 if category == "stylized" else -4
        if treatment_id in harder_lanes:
            score += 15 if style_mode == "luxury" else 11
        if mode == "men" and style_mode == "luxury":
            score += 12 if category == "stylized" else -10
            if treatment_id in {"direct_flash_night", "cinematic_poster_realism"}:
                score += 6
            if treatment_id == "clean_commercial":
                score -= 18
        if mode == "men" and style_mode == "romantic":
            score += 16 if category == "stylized" else -14
            if treatment_id in {"analog_35mm", "documentary_still", "disposable_camera", "candid_phone_snapshot", "low_key_dramatic", "direct_light_editorial"}:
                score += 12
            if treatment_id == "clean_commercial":
                score -= 22
        if mode == "women" and style_mode == "luxury":
            if treatment_id in {"direct_light_editorial", "concept_photo_editorial", "cinematic_poster_realism", "advertising_poster_realism", "vintage_flash_photo"}:
                score += 10
            if treatment_id == "clean_commercial":
                score -= 14
        if mode == "women" and style_mode == "romantic":
            if treatment_id in {"analog_35mm", "documentary_still", "candid_phone_snapshot", "disposable_camera", "direct_light_editorial", "cinematic_poster_realism"}:
                score += 10
            if treatment_id == "clean_commercial":
                score -= 18
        if style_mode == "luxury" and treatment_id in {"casual_indoor_selfie", "advertising_poster_realism", "vintage_flash_photo"}:
            score += 8
    elif style_mode in {"lifestyle", "urban_day"}:
        score += 7 if category == "stylized" else -2
        if treatment_id == "direct_light_editorial":
            score += 8
        if treatment_id in casual_stylized_lanes:
            score += 12
        if mode == "women" and treatment_id in {"candid_phone_snapshot", "analog_35mm", "documentary_still", "casual_indoor_selfie"}:
            score += 10
        if treatment_id == "clean_commercial":
            score -= 10
    elif style_mode in {"cultural_bookish", "creative_artistic"}:
        score += 8 if category == "stylized" else -2
        if treatment_id in casual_stylized_lanes:
            score += 10
        if style_mode == "creative_artistic" and treatment_id in {"concept_photo_editorial", "direct_light_editorial", "advertising_poster_realism"}:
            score += 8
        if style_mode == "creative_artistic" and treatment_id == "clean_commercial":
            score -= 8
    elif style_mode in {"sport", "fitness", "coastal", "vacation"}:
        score += 4 if category == "polished" else -1
        if style_mode == "fitness":
            if mode == "women":
                if category == "stylized":
                    score += 12
                if category == "polished":
                    score -= 6
                if treatment_id in {"candid_phone_snapshot", "analog_35mm", "documentary_still", "direct_light_editorial", "disposable_camera"}:
                    score += 16
                if scene_family == "wellness_spa" and treatment_id in {"candid_phone_snapshot", "analog_35mm", "documentary_still"}:
                    score += 8
                if treatment_id == "clean_commercial":
                    score -= 24
            else:
                if category == "stylized":
                    score += 5
                if treatment_id in {"candid_phone_snapshot", "analog_35mm", "documentary_still", "direct_light_editorial"}:
                    score += 10
                if treatment_id == "clean_commercial":
                    score -= 8
    if mode == "couples" and style_mode == "random":
        if category == "polished":
            score -= 12
        if category == "stylized":
            score += 16
        if treatment_id in {
            "candid_phone_snapshot",
            "casual_indoor_selfie",
            "mirror_selfie",
            "disposable_camera",
            "analog_35mm",
            "cinematic_poster_realism",
            "direct_light_editorial",
            "documentary_still",
            "concept_photo_editorial",
            "vintage_flash_photo",
            "advertising_poster_realism",
        }:
            score += 18
        if treatment_id == "clean_commercial":
            score -= 80
    return score


def _photo_treatment_batch_score(batch: list[dict[str, Any]], style_mode: str, mode: str = "women") -> int:
    return scoring._photo_treatment_batch_score(batch, style_mode, mode)
    targets = {
        "random": 0.65,
        "nightlife": 0.70,
        "studio": 0.65,
        "creative_artistic": 0.72,
        "luxury": 0.62,
        "romantic": 0.68,
        "old_money": 0.45,
        "lifestyle": 0.50,
        "urban_day": 0.50,
        "cultural_bookish": 0.50,
        "coastal": 0.40,
        "vacation": 0.40,
        "sport": 0.35,
        "fitness": 0.35,
    }
    target = targets.get(style_mode)
    if target is None:
        return 0
    if mode == "men" and style_mode == "luxury":
        target = 0.72
    if mode == "men" and style_mode == "romantic":
        target = 0.80
    if mode == "couples" and style_mode == "random":
        target = 0.62
    if mode == "women" and style_mode == "random":
        target = 0.62
    if mode == "women" and style_mode == "lifestyle":
        target = 0.68
    if mode == "women" and style_mode == "luxury":
        target = 0.70
    if mode == "women" and style_mode == "romantic":
        target = 0.82
    if mode == "women" and style_mode == "nightlife":
        target = 0.82
    if mode == "women" and style_mode == "creative_artistic":
        target = 0.80
    if mode == "women" and style_mode == "fitness":
        target = 0.78
    if mode == "men" and style_mode == "luxury":
        target = 0.70
    stylized_count = sum(1 for candidate in batch if candidate.get("photo_treatment_category") == "stylized")
    polished_count = sum(1 for candidate in batch if candidate.get("photo_treatment_category") == "polished")
    harder_lane_count = sum(1 for candidate in batch if candidate.get("photo_treatment_id") in {"concept_photo_editorial", "direct_light_editorial"})
    casual_lane_ids = {"mirror_selfie", "disposable_camera", "documentary_still", "casual_indoor_selfie", "vintage_flash_photo", "advertising_poster_realism"}
    casual_lane_count = sum(1 for candidate in batch if candidate.get("photo_treatment_id") in casual_lane_ids)
    unique_casual_lanes = len({candidate.get("photo_treatment_id") for candidate in batch if candidate.get("photo_treatment_id") in casual_lane_ids})
    unique_harder_lanes = len({candidate.get("photo_treatment_id") for candidate in batch if candidate.get("photo_treatment_id") in {"concept_photo_editorial", "direct_light_editorial"}})
    unique_lighting_count = len({candidate.get("lighting_family_id") for candidate in batch if candidate.get("lighting_family_id")})
    clean_count = sum(1 for candidate in batch if candidate.get("photo_treatment_id") == "clean_commercial")
    ratio = stylized_count / len(batch)
    diff = abs(ratio - target)
    expected_polished = len(batch) * (1 - target)
    polished_excess = max(0.0, polished_count - expected_polished)
    score = 52 - diff * 150 - polished_excess * 12
    score += min(unique_lighting_count, 5) * 3
    if style_mode == "random":
        score += min(harder_lane_count, 5) * 4
        score += unique_harder_lanes * 3
        score += min(casual_lane_count, 5) * 4
        score += unique_casual_lanes * 3
        if mode == "women":
            women_favored = sum(1 for candidate in batch if candidate.get("photo_treatment_id") in {"disposable_camera", "documentary_still", "mirror_selfie", "candid_phone_snapshot", "vintage_flash_photo", "advertising_poster_realism"})
            score += women_favored * 4
    elif style_mode == "luxury":
        score += min(harder_lane_count, 6) * 7
        score += unique_harder_lanes * 6
        if mode == "men":
            score += stylized_count * 2
            score -= polished_count
    elif style_mode in {"studio", "creative_artistic"}:
        score += min(harder_lane_count, 6) * 8
        score += unique_harder_lanes * 6
        score += min(casual_lane_count, 3) * 3
        if style_mode == "studio":
            poster_count = sum(1 for candidate in batch if candidate.get("photo_treatment_id") == "advertising_poster_realism")
            score += poster_count * 5
        if style_mode == "creative_artistic":
            vintage_count = sum(1 for candidate in batch if candidate.get("photo_treatment_id") == "vintage_flash_photo")
            score += vintage_count * 4
    elif style_mode in {"lifestyle", "urban_day"}:
        score += min(harder_lane_count, 3) * 4
        score += unique_harder_lanes * 3
        score += min(casual_lane_count, 5) * 5
        score += unique_casual_lanes * 4
        if mode == "women" and style_mode == "lifestyle":
            lifestyle_favored = sum(1 for candidate in batch if candidate.get("photo_treatment_id") in {"candid_phone_snapshot", "analog_35mm", "documentary_still", "disposable_camera", "casual_indoor_selfie", "direct_light_editorial"})
            score += lifestyle_favored * 4
    elif style_mode == "cultural_bookish":
        score += min(casual_lane_count, 5) * 5
        score += unique_casual_lanes * 5
    elif style_mode == "nightlife":
        vintage_count = sum(1 for candidate in batch if candidate.get("photo_treatment_id") == "vintage_flash_photo")
        score += vintage_count * 6
        if mode == "women":
            nightlife_favored = sum(
                1
                for candidate in batch
                if candidate.get("photo_treatment_id") in {"vintage_flash_photo", "direct_flash_night", "low_key_dramatic", "cinematic_poster_realism", "disposable_camera", "concept_photo_editorial"}
            )
            score += nightlife_favored * 5
    elif style_mode == "fitness":
        if mode == "women":
            fitness_favored = sum(1 for candidate in batch if candidate.get("photo_treatment_id") in {"candid_phone_snapshot", "analog_35mm", "documentary_still", "direct_light_editorial"})
            score += fitness_favored * 8
            score += min(casual_lane_count, 5) * 5
    if mode == "women" and style_mode == "romantic":
        romantic_favored = sum(
            1
            for candidate in batch
            if candidate.get("photo_treatment_id") in {"analog_35mm", "documentary_still", "candid_phone_snapshot", "disposable_camera", "direct_light_editorial", "cinematic_poster_realism"}
        )
        score += romantic_favored * 5
    if mode == "men" and style_mode == "romantic":
        documentary_count = sum(1 for candidate in batch if candidate.get("photo_treatment_id") in {"documentary_still", "analog_35mm", "disposable_camera", "direct_light_editorial"})
        score += documentary_count * 6
    if mode == "couples" and style_mode == "random":
        couples_favored_ids = {
            "candid_phone_snapshot",
            "casual_indoor_selfie",
            "mirror_selfie",
            "disposable_camera",
            "analog_35mm",
            "cinematic_poster_realism",
            "direct_light_editorial",
            "documentary_still",
            "concept_photo_editorial",
            "vintage_flash_photo",
            "advertising_poster_realism",
        }
        couples_favored = sum(1 for candidate in batch if candidate.get("photo_treatment_id") in couples_favored_ids)
        unique_couples_favored = len({candidate.get("photo_treatment_id") for candidate in batch if candidate.get("photo_treatment_id") in couples_favored_ids})
        score += couples_favored * 5
        score += unique_couples_favored * 3
    clean_caps: dict[tuple[str, str], int] = {
        ("women", "random"): 4,
        ("women", "luxury"): 4,
        ("women", "nightlife"): 2,
        ("women", "creative_artistic"): 3,
        ("women", "lifestyle"): 6,
        ("women", "fitness"): 3,
        ("women", "romantic"): 2,
        ("men", "luxury"): 3,
        ("men", "romantic"): 3,
        ("couples", "random"): 4,
    }
    clean_cap = clean_caps.get((mode, style_mode))
    if clean_cap is not None and clean_count > clean_cap:
        score -= (clean_count - clean_cap) * (18 if mode == "couples" and style_mode == "random" else 12)
    if style_mode == "random":
        polished_bonus = min(polished_count, 4)
        if polished_bonus:
            score += polished_bonus * (12 if mode == "couples" else 8)
    return int(round(score))


def _vibe_score(candidate: dict[str, Any], vibe: str) -> int:
    return scoring._vibe_score(candidate, vibe)
    mood = candidate["mood_energy_id"]
    capture = candidate["capture_style_id"]
    makeup = candidate["makeup_style_id"]
    lighting = candidate["lighting_family_id"]
    tags = set(candidate.get("tags", []))
    mapping = {
        "soft": int(mood == "soft_flirty") * 10 + int(lighting == "soft_overcast") * 8,
        "clean": int(lighting == "clean_daylight") * 10 + int("clean" in tags) * 6,
        "sexy": int(mood in {"soft_flirty", "slow_seductive"}) * 10 + int("slutty" in tags) * 6,
        "glam": int(makeup == "night_out_glam") * 10 + int(candidate["beauty_level_id"] == "beautified_glam") * 8,
        "cinematic": int(candidate["route"] == "cinematic_night") * 10 + int(capture == "editorial_photo") * 5,
        "casual": int(capture in {"lifestyle_photo", "smartphone_photo"}) * 10,
        "flirty": int(mood in {"soft_flirty", "bratty"}) * 10,
        "rich": int("luxury" in tags) * 10 + int(candidate["scene_family_id"] in {"residential_luxury", "hospitality_suite"}) * 6,
        "editorial": int(capture == "editorial_photo") * 12,
    }
    return mapping.get(vibe, 0)


def _framing_score(candidate: dict[str, Any], control: str) -> int:
    return scoring._framing_score(candidate, control)
    if control == "more_portraits":
        return 10 if framing in {"waist_up", "bust_up", "close_portrait", "head_and_shoulders"} else -4
    if control == "more_full_body":
        return 10 if framing in {"full_body", "cowboy_shot", "knee_up"} else -4
    return 0


def _lighting_score(candidate: dict[str, Any], control: str) -> int:
    return scoring._lighting_score(candidate, control)
    if control == "sunny":
        return 10 if lighting == "clean_daylight" else -3
    if control == "indoor_warm":
        return 10 if lighting == "warm_interior" else -3
    if control == "night":
        return 10 if lighting == "neon_night" else -3
    return 0


def _spicy_score(candidate: dict[str, Any], spicy_level: int) -> int:
    return scoring._spicy_score(candidate, spicy_level)


def _women_high_spicy_pose_mix_score(batch: list[dict[str, Any]], spicy_level: int) -> int:
    return scoring._women_high_spicy_pose_mix_score(batch, spicy_level)
    batch_size = len(batch)
    spicy_pose_ids = [candidate.get("pose_family_id") for candidate in batch if candidate.get("pose_family_id") in active_pose_ids]
    spicy_pose_count = len(spicy_pose_ids)
    unique_spicy_pose_count = len(set(spicy_pose_ids))
    target_spicy_count = math.ceil(batch_size * 0.65)
    ordinary_cap = batch_size - target_spicy_count
    score = min(spicy_pose_count, target_spicy_count) * 6
    score += unique_spicy_pose_count * 4
    if spicy_pose_count < target_spicy_count:
        score -= (target_spicy_count - spicy_pose_count) * 18
    ordinary_pose_count = batch_size - spicy_pose_count
    if ordinary_pose_count > ordinary_cap:
        score -= (ordinary_pose_count - ordinary_cap) * 12
    return score


def _candidate_text_blob(candidate: dict[str, Any]) -> str:
    return scoring._candidate_text_blob(candidate)


def _free_text_overlap_score(candidate: dict[str, Any], text: str, per_token: int, phrase_bonus: int = 0) -> int:
    return scoring._free_text_overlap_score(candidate, text, per_token, phrase_bonus)
    blob = _candidate_text_blob(candidate)
    score = phrase_bonus if cleaned.lower() in blob else 0
    for token in _tokenize_text(cleaned):
        if token in blob:
            score += per_token
    return score


def _appearance_text_score(candidate: dict[str, Any], text: str) -> int:
    return scoring._appearance_text_score(candidate, text)


def _appearance_prompt_profile(text: str) -> dict[str, bool]:
    return scoring._appearance_prompt_profile(text)


def _appearance_profile_score(candidate: dict[str, Any], text: str) -> int:
    return scoring._appearance_profile_score(candidate, text)
    profile = _appearance_prompt_profile(text)
    score = 0
    tags = set(candidate.get("tags", []))
    mood = candidate.get("mood_energy_id")
    pose = candidate.get("pose_family_id")
    hand = candidate.get("hand_action_id")
    scene = candidate.get("scene_family_id")
    route = candidate.get("route")
    if profile["reserved"]:
        score += 8 if "reserved" in tags else 0
        score += 12 if mood == "calm_confident" else 5 if mood == "soft_flirty" else -16 if mood in {"slow_seductive", "bratty"} else 0
        score -= 16 if pose in LOW_SPICY_UNSAFE_POSE_IDS else 0
        score -= 8 if hand in {"hand_on_thigh", "touching_strap", "hooked_waistband"} else 0
        score -= 18 if scene in {"nightlife_bar", "nightlife_neon"} else 0
        score -= 12 if route == "cinematic_night" else 0
    if profile["sporty"]:
        score += 12 if scene == "urban_daylight" else -6
        score += 10 if route == "sports_flirt" else -6
        score += 8 if {"sporty", "athletic"} & tags else 0
    if profile["nightlife"]:
        score += 12 if scene in {"nightlife_bar", "nightlife_neon"} else -8
        score += 10 if route == "cinematic_night" else -5
    return score


def _scene_focus_score(candidate: dict[str, Any], scene_focus: str) -> int:
    return scoring._scene_focus_score(candidate, scene_focus)
    profile = SCENE_FOCUS_PREFERENCES.get(scene_focus)
    if not profile:
        return 0
    score = 0
    tags = set(candidate.get("tags", []))
    if candidate.get("scene_family_id") in profile.get("required_scene_families", set()):
        score += 18
    else:
        score -= 14
    if candidate.get("route") in profile.get("preferred_route_ids", set()):
        score += 10
    if candidate.get("capture_style_id") in profile.get("preferred_capture_ids", set()):
        score += 6
    if tags & profile.get("preferred_tags", set()):
        score += 6
    return score


def _women_scene_family_score(candidate: dict[str, Any], scene_family_id: str) -> int:
    return scoring._women_scene_family_score(candidate, scene_family_id)
    return 30 if candidate.get("scene_family_id") == scene_family_id else -18


def _women_scene_family_batch_score(batch: list[dict[str, Any]], scene_family_id: str) -> int:
    return scoring._women_scene_family_batch_score(batch, scene_family_id)
    matching = sum(1 for candidate in batch if candidate.get("scene_family_id") == scene_family_id)
    return (matching * 20) - ((len(batch) - matching) * 12)


def _infer_theme_style_mode(form_state: dict[str, Any]) -> str:
    return form_runtime_controls._infer_theme_style_mode(form_state)


def infer_theme_style_mode(form_state: dict[str, Any]) -> str:
    return _infer_theme_style_mode(form_state)


def _matched_theme_hints(exact_theme: str) -> list[dict[str, Any]]:
    return form_runtime_controls._matched_theme_hints(exact_theme)


def _exact_theme_scene_constraints(form_state: dict[str, Any]) -> tuple[set[str], set[str]]:
    return form_runtime_controls._exact_theme_scene_constraints(form_state)


def _effective_outfit_reveal(form_state: dict[str, Any], spicy_level: int) -> str:
    return form_runtime_controls._effective_outfit_reveal(form_state, spicy_level)


def _effective_makeup_control(form_state: dict[str, Any], spicy_level: int) -> str:
    return form_runtime_controls._effective_makeup_control(form_state, spicy_level)


def _merge_preference_sets(*values: set[str]) -> set[str]:
    return form_user_profile._merge_preference_sets(*values)


def _user_style_profile(form_state: dict[str, Any], spicy_level: int) -> dict[str, Any]:
    return form_user_profile._user_style_profile(form_state, spicy_level)


def _exact_theme_score(candidate: dict[str, Any], exact_theme: str, location_strategy: str) -> int:
    return scoring._exact_theme_score(candidate, exact_theme, location_strategy)
    per_token = 10 if location_strategy == "exact_theme" else 5
    phrase_bonus = 24 if location_strategy == "exact_theme" else 10
    score = _free_text_overlap_score(candidate, exact_theme, per_token=per_token, phrase_bonus=phrase_bonus)
    matched_hints = _matched_theme_hints(exact_theme)
    tags = set(candidate.get("tags", []))
    for hint in matched_hints:
        if candidate.get("scene_family_id") in hint["scene_families"]:
            score += 18 if location_strategy == "exact_theme" else 8
        if candidate.get("route") in hint["routes"]:
            score += 16 if location_strategy == "exact_theme" else 6
        if tags & hint["tags"]:
            score += 10 if location_strategy == "exact_theme" else 4
    return score


def _exact_theme_batch_score(batch: list[dict[str, Any]], exact_theme: str, location_strategy: str) -> int:
    return scoring._exact_theme_batch_score(batch, exact_theme, location_strategy)
    matched_hints = _matched_theme_hints(exact_theme)
    if not matched_hints:
        return 0
    preferred_scenes = set().union(*(hint["scene_families"] for hint in matched_hints))
    preferred_routes = set().union(*(hint["routes"] for hint in matched_hints))
    preferred_tags = set().union(*(hint["tags"] for hint in matched_hints))
    score = 0
    for candidate in batch:
        tags = set(candidate.get("tags", []))
        matches = (
            candidate.get("scene_family_id") in preferred_scenes
            or candidate.get("route") in preferred_routes
            or bool(tags & preferred_tags)
        )
        score += 26 if matches else -16
    return score


def _outfit_reveal_score(candidate: dict[str, Any], reveal_mode: str) -> int:
    return scoring._outfit_reveal_score(candidate, reveal_mode)
    tags = set(candidate.get("tags", []))
    if reveal_mode == "reserved":
        return 18 if "reserved" in tags else -10
    if reveal_mode == "balanced":
        return 12 if "balanced_reveal" in tags or candidate.get("outfit_family_id") in {"mini_dress", "cardigan_trousers", "blouse_trousers", "knit_top_trousers", "silk_blouse_midi_skirt", "structured_day_dress"} else -4
    if reveal_mode == "revealing":
        return 14 if "revealing" in tags or candidate.get("outfit_family_id") == "crop_top_mini_skirt" else -5
    if reveal_mode == "pushing_it":
        return 16 if "pushing_it" in tags or candidate.get("outfit_family_id") in {"latex_editorial", "bikini_set"} else -8
    return 0


def _hair_atom_score(candidate: dict[str, Any], form_state: dict[str, Any]) -> int:
    return scoring._hair_atom_score(candidate, form_state)
    if form_state["hairstyle"] not in {"random", "custom"}:
        score += 18 if hair_structure_id == form_state["hairstyle"] else -10
    elif form_state["hairLength"] in HAIR_LENGTH_PREFERENCES:
        score += 12 if hair_structure_id in HAIR_LENGTH_PREFERENCES[form_state["hairLength"]] else -6
    if form_state["hairColorControl"] in HAIR_COLOR_PREFERENCES:
        preferred = HAIR_COLOR_PREFERENCES[form_state["hairColorControl"]]
        score += 16 if hair_color_id in preferred else -8
    if form_state["hairstyle"] == "custom" and form_state.get("customHair"):
        score += _free_text_overlap_score(candidate, form_state["customHair"], per_token=5, phrase_bonus=12)
    if form_state["hairColorControl"] == "custom" and form_state.get("customHairColor"):
        score += _free_text_overlap_score(candidate, form_state["customHairColor"], per_token=6, phrase_bonus=14)
    if form_state["hairColorControl"] == "random" and "vivid_colored_hair" in hair_tags:
        score -= 12
    return score


def _makeup_atom_score(candidate: dict[str, Any], makeup_control: str) -> int:
    return scoring._makeup_atom_score(candidate, makeup_control)
    return 16 if candidate.get("makeup_style_id") == makeup_control else -8


def _eye_color_score(candidate: dict[str, Any], control: str) -> int:
    return scoring._eye_color_score(candidate, control)
    return 16 if candidate.get("eye_color_id") == control else -8


def _breast_size_score(candidate: dict[str, Any], control: str) -> int:
    return scoring._breast_size_score(candidate, control)
    return 18 if candidate.get("breast_size_id") == control else -12


def _character_constraint_score(candidate: dict[str, Any], character_constraint: str) -> int:
    return scoring._character_constraint_score(candidate, character_constraint)
    return _free_text_overlap_score(candidate, character_constraint, per_token=3, phrase_bonus=6)


def _validation_penalty(findings_count: int, mode: str) -> int:
    return scoring._validation_penalty(findings_count, mode)
    if mode == "strict":
        return -500 * findings_count
    return -120 * findings_count


def _anti_repeat_score(batch: list[dict[str, Any]], anti_repeat_mode: str) -> int:
    return scoring._anti_repeat_score(batch, anti_repeat_mode)
    for field_name, penalty in profile["field_penalties"].items():
        counts = Counter(candidate.get(field_name) for candidate in batch if candidate.get(field_name))
        duplicates = sum(count - 1 for count in counts.values() if count > 1)
        score -= duplicates * penalty
    score += len({candidate["scene_family_id"] for candidate in batch}) * profile["unique_scene_bonus"]
    score += len({candidate["setting_micro_id"] for candidate in batch}) * profile["unique_setting_bonus"]
    combo_counts = Counter(
        (
            candidate.get("outfit_family_id"),
            candidate.get("material_id"),
            candidate.get("color_story_id"),
        )
        for candidate in batch
    )
    combo_penalty_map = {"low": 10, "normal": 20, "hard": 32, "brutal": 48}
    combo_penalty = combo_penalty_map.get(anti_repeat_mode, 12)
    score -= sum(count - 1 for count in combo_counts.values() if count > 1) * combo_penalty
    return score


def _apply_prompt_constraints(candidate: dict[str, Any], form_state: dict[str, Any], spicy_level: int) -> dict[str, Any]:
    return postprocess._apply_prompt_constraints(candidate, form_state, spicy_level)
    if (
        form_state.get("mode") == "couples"
        and form_state.get("styleMode") == "lifestyle"
        and constrained.get("photo_treatment_id") == "clean_commercial"
    ):
        constrained = _remap_couples_lifestyle_treatment(constrained)
    if (
        form_state.get("mode") == "men"
        and form_state.get("styleMode") == "random"
        and constrained.get("photo_treatment_id") == "clean_commercial"
    ):
        constrained = _remap_men_random_treatment(constrained)
    if (
        form_state.get("mode") == "men"
        and form_state.get("styleMode") == "nightlife"
        and constrained.get("photo_treatment_id") == "clean_commercial"
    ):
        constrained = _remap_men_nightlife_treatment(constrained)
    if (
        form_state.get("mode") == "men"
        and form_state.get("styleMode") == "romantic"
        and constrained.get("photo_treatment_id") == "clean_commercial"
    ):
        constrained = _remap_men_romantic_treatment(constrained)
    if (
        form_state.get("mode") == "women"
        and form_state.get("styleMode") == "random"
        and constrained.get("photo_treatment_id") == "clean_commercial"
    ):
        constrained = _remap_women_random_treatment(constrained)
    if (
        form_state.get("mode") == "women"
        and form_state.get("styleMode") == "lifestyle"
        and constrained.get("photo_treatment_id") == "clean_commercial"
    ):
        constrained = _remap_women_lifestyle_treatment(constrained)
    if (
        form_state.get("mode") == "women"
        and form_state.get("styleMode") == "romantic"
        and constrained.get("photo_treatment_id") == "clean_commercial"
    ):
        constrained = _remap_women_romantic_treatment(constrained)
    if (
        form_state.get("mode") == "women"
        and form_state.get("styleMode") == "fitness"
        and constrained.get("photo_treatment_id") == "clean_commercial"
    ):
        constrained = _remap_women_fitness_treatment(constrained)
    if (
        form_state.get("mode") == "women"
        and form_state.get("styleMode") == "nightlife"
        and constrained.get("photo_treatment_id") == "clean_commercial"
    ):
        constrained = _remap_women_nightlife_treatment(constrained)
    if (
        form_state.get("mode") == "women"
        and form_state.get("styleMode") == "luxury"
        and constrained.get("photo_treatment_id") == "clean_commercial"
    ):
        constrained = _remap_women_luxury_treatment(constrained)
    if (
        form_state.get("mode") == "women"
        and form_state.get("styleMode") == "creative_artistic"
        and constrained.get("photo_treatment_id") == "clean_commercial"
    ):
        constrained = _remap_women_creative_treatment(constrained)
    if (
        form_state.get("mode") == "couples"
        and form_state.get("styleMode") == "random"
        and constrained.get("photo_treatment_id") == "clean_commercial"
    ):
        constrained = _remap_couples_random_treatment(constrained)
    if form_state.get("mode") == "women" and form_state.get("styleMode") == "nightlife" and constrained.get("material_id") == "vinyl_latex":
        constrained["material_id"] = "satin"
        constrained["material"] = "satin finish"
    if spicy_level <= 3 and constrained.get("pose_family_id") in LOW_SPICY_UNSAFE_POSE_IDS:
        constrained["pose_family_id"] = "seated_sideways"
        constrained["pose_family"] = "seated sideways with both legs angled to one side"
    if spicy_level <= 3 and constrained.get("hand_action_id") in {"hand_on_thigh", "touching_strap", "hooked_waistband"}:
        constrained["hand_action_id"] = "hand_at_waist"
        constrained["hand_action"] = "one hand at her waist"
    if form_state.get("name"):
        constrained["subject_name"] = form_state["name"]
    if female_custom_appearance:
        constrained["appearance_prompt"] = _female_appearance_prompt(form_state)
    if form_state.get("racePreset") == "other" and form_state.get("customRace"):
        constrained["ethnicity_override"] = form_state["customRace"]
    if form_state.get("exactTheme"):
        constrained["exact_theme"] = form_state["exactTheme"]
    if form_state.get("characterConstraint"):
        constrained["character_constraint"] = form_state["characterConstraint"]
    if (
        form_state.get("personMode") == "same_person"
        and form_state.get("useCoreIdentityPrompt")
        and form_state.get("coreIdentityPrompt")
    ):
        constrained["core_identity_prompt"] = form_state["coreIdentityPrompt"]
    if not female_custom_appearance and form_state.get("hairstyle") == "custom" and form_state.get("customHair"):
        constrained["hair_structure_override"] = form_state["customHair"]
    if not female_custom_appearance and form_state.get("hairColorControl") == "custom" and form_state.get("customHairColor"):
        constrained["hair_color_override"] = form_state["customHairColor"]
    return constrained


def _remap_couples_random_treatment(candidate: dict[str, Any]) -> dict[str, Any]:
    scene_family = str(candidate.get("scene_family_id", "") or "")
    style_mode = "random"
    remap_seed = "|".join(
        str(candidate.get(key, "") or "")
        for key in (
            "scene_family_id",
            "setting_scene_id",
            "camera_framing_id",
            "outfit_family_id",
            "color_story_id",
            "age_band",
        )
    )
    keep_probability = 1.0
    if random.Random(remap_seed).random() < keep_probability:
        return candidate
    if scene_family in {"nightlife_bar", "nightlife_neon"}:
        preferred_ids = ["vintage_flash_photo", "direct_flash_night", "cinematic_poster_realism", "documentary_still"]
    elif scene_family in {"residential_luxury", "hospitality_suite", "grooming_bath"}:
        preferred_ids = ["casual_indoor_selfie", "mirror_selfie", "candid_phone_snapshot", "analog_35mm"]
    elif scene_family in {"studio", "creative_gallery"}:
        preferred_ids = ["concept_photo_editorial", "direct_light_editorial", "advertising_poster_realism", "documentary_still"]
    else:
        preferred_ids = ["candid_phone_snapshot", "disposable_camera", "documentary_still", "analog_35mm", "direct_light_editorial"]

    lookup = _photo_treatment_lookup()
    chosen_profile: dict[str, Any] | None = None
    for treatment_id in preferred_ids:
        profile = lookup.get(treatment_id)
        if not profile:
            continue
        allowed_scenes = {str(value) for value in profile.get("allowed_scene_families", [])}
        banned_scenes = {str(value) for value in profile.get("banned_scene_families", [])}
        allowed_styles = {str(value) for value in profile.get("allowed_style_modes", [])}
        banned_styles = {str(value) for value in profile.get("banned_style_modes", [])}
        if allowed_scenes and scene_family not in allowed_scenes:
            continue
        if scene_family in banned_scenes:
            continue
        if allowed_styles and style_mode not in allowed_styles:
            continue
        if style_mode in banned_styles:
            continue
        chosen_profile = profile
        break
    if not chosen_profile:
        return candidate

    remapped = dict(candidate)
    remapped["photo_treatment_id"] = chosen_profile["id"]
    remapped["photo_treatment"] = chosen_profile.get("label", chosen_profile["id"])
    remapped["photo_treatment_category"] = chosen_profile.get("category", "stylized")
    remapped["capture_style_render"] = chosen_profile.get("capture_render", remapped.get("capture_style_render", remapped.get("capture_style", "photo")))
    remapped["lighting_render"] = chosen_profile.get("lighting_render", remapped.get("lighting_render", remapped.get("lighting_family", "")))
    remapped["camera_vibe"] = chosen_profile.get("camera_vibe", "")
    remapped["color_grade"] = chosen_profile.get("color_grade", "")
    remapped["finish_render"] = chosen_profile.get("finish", remapped.get("finish_render", "natural skin texture"))
    return remapped


def _remap_women_fitness_treatment(candidate: dict[str, Any]) -> dict[str, Any]:
    scene_family = str(candidate.get("scene_family_id", "") or "")
    style_mode = "fitness"
    if scene_family == "wellness_spa":
        preferred_ids = ["candid_phone_snapshot", "analog_35mm", "documentary_still"]
    else:
        preferred_ids = ["candid_phone_snapshot", "analog_35mm", "direct_light_editorial", "documentary_still"]

    lookup = _photo_treatment_lookup()
    chosen_profile: dict[str, Any] | None = None
    for treatment_id in preferred_ids:
        profile = lookup.get(treatment_id)
        if not profile:
            continue
        allowed_scenes = {str(value) for value in profile.get("allowed_scene_families", [])}
        banned_scenes = {str(value) for value in profile.get("banned_scene_families", [])}
        allowed_styles = {str(value) for value in profile.get("allowed_style_modes", [])}
        banned_styles = {str(value) for value in profile.get("banned_style_modes", [])}
        if allowed_scenes and scene_family not in allowed_scenes:
            continue
        if scene_family in banned_scenes:
            continue
        if allowed_styles and style_mode not in allowed_styles:
            continue
        if style_mode in banned_styles:
            continue
        chosen_profile = profile
        break
    if not chosen_profile:
        return candidate

    remapped = dict(candidate)
    remapped["photo_treatment_id"] = chosen_profile["id"]
    remapped["photo_treatment"] = chosen_profile.get("label", chosen_profile["id"])
    remapped["photo_treatment_category"] = chosen_profile.get("category", "stylized")
    remapped["capture_style_render"] = chosen_profile.get("capture_render", remapped.get("capture_style_render", remapped.get("capture_style", "photo")))
    remapped["lighting_render"] = chosen_profile.get("lighting_render", remapped.get("lighting_render", remapped.get("lighting_family", "")))
    remapped["camera_vibe"] = chosen_profile.get("camera_vibe", "")
    remapped["color_grade"] = chosen_profile.get("color_grade", "")
    remapped["finish_render"] = chosen_profile.get("finish", remapped.get("finish_render", "natural skin texture"))
    return remapped


def _remap_women_lifestyle_treatment(candidate: dict[str, Any]) -> dict[str, Any]:
    scene_family = str(candidate.get("scene_family_id", "") or "")
    style_mode = "lifestyle"
    remap_seed = "|".join(
        str(candidate.get(key, "") or "")
        for key in (
            "scene_family_id",
            "setting_scene_id",
            "camera_framing_id",
            "outfit_family_id",
            "color_story_id",
            "age_band",
        )
    )
    if random.Random(remap_seed).random() > 0.68:
        return candidate
    if scene_family in {"culture_bookish", "garden_conservatory"}:
        preferred_ids = ["analog_35mm", "documentary_still", "casual_indoor_selfie", "candid_phone_snapshot"]
    elif scene_family in {"urban_daylight", "courtyard_garden"}:
        preferred_ids = ["candid_phone_snapshot", "disposable_camera", "analog_35mm", "direct_light_editorial"]
    else:
        preferred_ids = ["candid_phone_snapshot", "analog_35mm", "documentary_still", "casual_indoor_selfie"]

    lookup = _photo_treatment_lookup()
    chosen_profile: dict[str, Any] | None = None
    for treatment_id in preferred_ids:
        profile = lookup.get(treatment_id)
        if not profile:
            continue
        allowed_scenes = {str(value) for value in profile.get("allowed_scene_families", [])}
        banned_scenes = {str(value) for value in profile.get("banned_scene_families", [])}
        allowed_styles = {str(value) for value in profile.get("allowed_style_modes", [])}
        banned_styles = {str(value) for value in profile.get("banned_style_modes", [])}
        if allowed_scenes and scene_family not in allowed_scenes:
            continue
        if scene_family in banned_scenes:
            continue
        if allowed_styles and style_mode not in allowed_styles:
            continue
        if style_mode in banned_styles:
            continue
        chosen_profile = profile
        break
    if not chosen_profile:
        return candidate

    remapped = dict(candidate)
    remapped["photo_treatment_id"] = chosen_profile["id"]
    remapped["photo_treatment"] = chosen_profile.get("label", chosen_profile["id"])
    remapped["photo_treatment_category"] = chosen_profile.get("category", "stylized")
    remapped["capture_style_render"] = chosen_profile.get("capture_render", remapped.get("capture_style_render", remapped.get("capture_style", "photo")))
    remapped["lighting_render"] = chosen_profile.get("lighting_render", remapped.get("lighting_render", remapped.get("lighting_family", "")))
    remapped["camera_vibe"] = chosen_profile.get("camera_vibe", "")
    remapped["color_grade"] = chosen_profile.get("color_grade", "")
    remapped["finish_render"] = chosen_profile.get("finish", remapped.get("finish_render", "natural skin texture"))
    return remapped


def _remap_women_random_treatment(candidate: dict[str, Any]) -> dict[str, Any]:
    return postprocess._remap_women_random_treatment(candidate)


def _remap_women_romantic_treatment(candidate: dict[str, Any]) -> dict[str, Any]:
    return postprocess._remap_women_romantic_treatment(candidate)


def _remap_women_nightlife_treatment(candidate: dict[str, Any]) -> dict[str, Any]:
    scene_family = str(candidate.get("scene_family_id", "") or "")
    style_mode = "nightlife"
    remap_seed = "|".join(
        str(candidate.get(key, "") or "")
        for key in (
            "scene_family_id",
            "setting_scene_id",
            "camera_framing_id",
            "outfit_family_id",
            "color_story_id",
            "age_band",
        )
    )
    if random.Random(remap_seed).random() > 0.86:
        return candidate
    if scene_family in {"nightlife_bar", "nightlife_neon"}:
        preferred_ids = ["vintage_flash_photo", "direct_flash_night", "cinematic_poster_realism", "low_key_dramatic", "disposable_camera"]
    else:
        preferred_ids = ["vintage_flash_photo", "cinematic_poster_realism", "low_key_dramatic", "documentary_still"]

    return _remap_treatment_by_preferences(candidate, preferred_ids, style_mode)


def _remap_women_luxury_treatment(candidate: dict[str, Any]) -> dict[str, Any]:
    return postprocess._remap_women_luxury_treatment(candidate)


def _remap_women_creative_treatment(candidate: dict[str, Any]) -> dict[str, Any]:
    scene_family = str(candidate.get("scene_family_id", "") or "")
    style_mode = "creative_artistic"
    remap_seed = "|".join(
        str(candidate.get(key, "") or "")
        for key in (
            "scene_family_id",
            "setting_scene_id",
            "camera_framing_id",
            "outfit_family_id",
            "color_story_id",
            "age_band",
        )
    )
    if random.Random(remap_seed).random() > 0.80:
        return candidate
    if scene_family in {"creative_gallery", "studio"}:
        preferred_ids = ["concept_photo_editorial", "direct_light_editorial", "advertising_poster_realism", "vintage_flash_photo", "documentary_still"]
    else:
        preferred_ids = ["direct_light_editorial", "documentary_still", "vintage_flash_photo", "analog_35mm"]

    return _remap_treatment_by_preferences(candidate, preferred_ids, style_mode)


def _remap_treatment_by_preferences(candidate: dict[str, Any], preferred_ids: list[str], style_mode: str) -> dict[str, Any]:
    scene_family = str(candidate.get("scene_family_id", "") or "")
    lookup = _photo_treatment_lookup()
    chosen_profile: dict[str, Any] | None = None
    for treatment_id in preferred_ids:
        profile = lookup.get(treatment_id)
        if not profile:
            continue
        allowed_scenes = {str(value) for value in profile.get("allowed_scene_families", [])}
        banned_scenes = {str(value) for value in profile.get("banned_scene_families", [])}
        allowed_styles = {str(value) for value in profile.get("allowed_style_modes", [])}
        banned_styles = {str(value) for value in profile.get("banned_style_modes", [])}
        if allowed_scenes and scene_family not in allowed_scenes:
            continue
        if scene_family in banned_scenes:
            continue
        if allowed_styles and style_mode not in allowed_styles:
            continue
        if style_mode in banned_styles:
            continue
        chosen_profile = profile
        break
    if not chosen_profile:
        return candidate

    remapped = dict(candidate)
    remapped["photo_treatment_id"] = chosen_profile["id"]
    remapped["photo_treatment"] = chosen_profile.get("label", chosen_profile["id"])
    remapped["photo_treatment_category"] = chosen_profile.get("category", "stylized")
    remapped["capture_style_render"] = chosen_profile.get("capture_render", remapped.get("capture_style_render", remapped.get("capture_style", "photo")))
    remapped["lighting_render"] = chosen_profile.get("lighting_render", remapped.get("lighting_render", remapped.get("lighting_family", "")))
    remapped["camera_vibe"] = chosen_profile.get("camera_vibe", "")
    remapped["color_grade"] = chosen_profile.get("color_grade", "")
    remapped["finish_render"] = chosen_profile.get("finish", remapped.get("finish_render", "natural skin texture"))
    return remapped


def _remap_men_random_treatment(candidate: dict[str, Any]) -> dict[str, Any]:
    scene_family = str(candidate.get("scene_family_id", "") or "")
    style_mode = "random"
    remap_seed = "|".join(
        str(candidate.get(key, "") or "")
        for key in (
            "scene_family_id",
            "setting_scene_id",
            "camera_framing_id",
            "outfit_family_id",
            "color_story_id",
            "age_band",
        )
    )
    if random.Random(remap_seed).random() > 0.58:
        return candidate
    if scene_family in {"nightlife_bar", "nightlife_neon"}:
        preferred_ids = ["vintage_flash_photo", "direct_flash_night", "candid_phone_snapshot", "cinematic_poster_realism"]
    elif scene_family in {"residential_luxury", "hospitality_suite", "grooming_bath"}:
        preferred_ids = ["casual_indoor_selfie", "mirror_selfie", "direct_light_editorial", "analog_35mm"]
    elif scene_family in {"creative_gallery", "studio"}:
        preferred_ids = ["concept_photo_editorial", "direct_light_editorial", "advertising_poster_realism", "documentary_still"]
    else:
        preferred_ids = ["candid_phone_snapshot", "analog_35mm", "documentary_still", "direct_light_editorial"]
    return _remap_treatment_by_preferences(candidate, preferred_ids, style_mode)


def _remap_men_nightlife_treatment(candidate: dict[str, Any]) -> dict[str, Any]:
    scene_family = str(candidate.get("scene_family_id", "") or "")
    style_mode = "nightlife"
    remap_seed = "|".join(
        str(candidate.get(key, "") or "")
        for key in (
            "scene_family_id",
            "setting_scene_id",
            "camera_framing_id",
            "outfit_family_id",
            "color_story_id",
            "age_band",
        )
    )
    if random.Random(remap_seed).random() > 0.62:
        return candidate
    if scene_family in {"nightlife_bar", "nightlife_neon"}:
        preferred_ids = ["vintage_flash_photo", "direct_flash_night", "candid_phone_snapshot", "disposable_camera", "cinematic_poster_realism", "low_key_dramatic"]
    else:
        preferred_ids = ["candid_phone_snapshot", "vintage_flash_photo", "cinematic_poster_realism", "low_key_dramatic"]
    return _remap_treatment_by_preferences(candidate, preferred_ids, style_mode)


def _remap_men_romantic_treatment(candidate: dict[str, Any]) -> dict[str, Any]:
    scene_family = str(candidate.get("scene_family_id", "") or "")
    style_mode = "romantic"
    remap_seed = "|".join(
        str(candidate.get(key, "") or "")
        for key in (
            "scene_family_id",
            "setting_scene_id",
            "camera_framing_id",
            "color_story_id",
            "lighting_family_id",
        )
    )
    if random.Random(remap_seed).random() > 0.78:
        return candidate
    if scene_family in {"garden_conservatory", "courtyard_garden"}:
        preferred_ids = ["analog_35mm", "documentary_still", "candid_phone_snapshot", "direct_light_editorial", "low_key_dramatic"]
    elif scene_family in {"residential_luxury", "hospitality_suite"}:
        preferred_ids = ["casual_indoor_selfie", "analog_35mm", "direct_light_editorial", "documentary_still", "low_key_dramatic"]
    else:
        preferred_ids = ["analog_35mm", "documentary_still", "direct_light_editorial", "candid_phone_snapshot", "low_key_dramatic"]
    return _remap_treatment_by_preferences(candidate, preferred_ids, style_mode)


def _remap_couples_lifestyle_treatment(candidate: dict[str, Any]) -> dict[str, Any]:
    scene_family = str(candidate.get("scene_family_id", "") or "")
    style_mode = "lifestyle"
    remap_seed = "|".join(
        str(candidate.get(key, "") or "")
        for key in (
            "scene_family_id",
            "setting_scene_id",
            "camera_framing_id",
            "outfit_family_id",
            "color_story_id",
            "age_band",
        )
    )
    if random.Random(remap_seed).random() > 0.66:
        return candidate
    if scene_family in {"culture_bookish", "garden_conservatory"}:
        preferred_ids = ["analog_35mm", "documentary_still", "candid_phone_snapshot", "casual_indoor_selfie"]
    elif scene_family in {"urban_daylight", "courtyard_garden"}:
        preferred_ids = ["candid_phone_snapshot", "disposable_camera", "analog_35mm", "direct_light_editorial"]
    else:
        preferred_ids = ["candid_phone_snapshot", "analog_35mm", "documentary_still", "casual_indoor_selfie"]
    return _remap_treatment_by_preferences(candidate, preferred_ids, style_mode)


def _diversify_women_outfit_colors(prompts: list[dict[str, Any]], form_state: dict[str, Any], spicy_level: int) -> list[dict[str, Any]]:
    return postprocess._diversify_women_outfit_colors(prompts, form_state, spicy_level)


def _diversify_couples_candidate_colors(
    scaffolds: list[dict[str, Any]],
    form_state: dict[str, Any],
    spicy_level: int,
) -> list[dict[str, Any]]:
    return postprocess._diversify_couples_candidate_colors(scaffolds, form_state, spicy_level)


def get_bootstrap() -> dict[str, Any]:
    from .services.bootstrap_service import get_bootstrap as get_bootstrap_service

    return get_bootstrap_service()


def generate_run(form_payload: dict[str, Any] | None) -> dict[str, Any]:
    from .services.run_service import generate_run as run_service_generate_run

    return run_service_generate_run(form_payload)


def save_preset_record(name: str, form_state: dict[str, Any]) -> dict[str, Any]:
    from .services.preset_service import save_preset_record as save_preset_record_service

    return save_preset_record_service(name, form_state)


def delete_preset_record(preset_id: str) -> None:
    from .services.preset_service import delete_preset_record as delete_preset_record_service

    delete_preset_record_service(preset_id)
