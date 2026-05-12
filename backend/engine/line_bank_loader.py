from __future__ import annotations

import hashlib
import re
from functools import lru_cache
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DATA_ROOT = ROOT / "data"
LINE_BANK_ROOT = DATA_ROOT / "overrides" / "line_banks"
SUPPORTED_GENDER_DOMAINS = {
    "women": ("poses", "expressions", "outfits"),
    "men": ("poses", "expressions", "outfits"),
    "couples": ("poses",),
}
SUPPORTED_GENDERS = tuple(SUPPORTED_GENDER_DOMAINS)
SUPPORTED_SHARED_GROUPS = ("shared",)
SUPPORTED_SHARED_DOMAINS = ("locations",)
SHARED_GLOBAL_FILENAMES = {"locations": "all"}
SHARED_LOCATION_DOMAIN_BY_FILENAME = {
    "all": "realism",
    "fantasy_locations": "fantasy_sci_fi",
}
BUCKET_RANGES = {
    "1_3": (1, 3),
    "4_5": (4, 5),
    "6_8": (6, 8),
}
DOMAIN_SPECS = {
    "poses": {
        "char_cap": 140,
        "min_chars": 12,
        "weight": 0.08,
        "id_prefix": "line_pose",
        "domain_tag": "pose",
        "extra_tags": [],
    },
    "expressions": {
        "char_cap": 120,
        "min_chars": 8,
        "weight": 0.08,
        "id_prefix": "line_expression",
        "domain_tag": "expression",
        "extra_tags": [],
    },
    "outfits": {
        "char_cap": 160,
        "min_chars": 12,
        "weight": 0.06,
        "id_prefix": "line_outfit",
        "domain_tag": "outfit",
        "extra_tags": ["needs_review_defaults"],
    },
    "locations": {
        "char_cap": 140,
        "min_chars": 12,
        "weight": 0.06,
        "id_prefix": "line_location",
        "domain_tag": "location",
        "extra_tags": [],
    },
}
DOMAIN_VOLUME_WARNING_THRESHOLD = 200
PRIVATE_OUTFIT_SCENES = {
    "grooming_bath",
    "wellness_spa",
    "studio",
    "coastal_pool",
    "nightlife_neon",
}
RESORT_SWIM_SCENES = {
    "coastal_pool",
    "coastal_boardwalk",
}
ROBE_OK_SCENES = {
    "grooming_bath",
    "wellness_spa",
}
LATEX_OK_SCENES = {
    "studio",
    "nightlife_neon",
    "nightlife_bar",
    "creative_gallery",
}
PUBLIC_RISKY_OK_SCENES = {
    "studio",
    "nightlife_neon",
    "nightlife_bar",
    "coastal_pool",
}
WET_OUTFIT_CONTEXT_SCENES = {
    "coastal_pool",
    "coastal_boardwalk",
    "wellness_spa",
    "grooming_bath",
}
WET_OUTFIT_CONTEXT_TAGS = {"pool", "beach", "spa", "shower", "rain", "humid", "wet_friendly"}
TIGHT_POSE_CROP_FRAMING_IDS = {"close_portrait", "head_and_shoulders", "face_only", "bust_up", "below_chest_portrait", "waist_up"}


def _empty_records() -> dict[str, dict[str, list[dict[str, Any]]]]:
    records = {
        gender: {domain: [] for domain in domains}
        for gender, domains in SUPPORTED_GENDER_DOMAINS.items()
    }
    records["shared"] = {domain: [] for domain in SUPPORTED_SHARED_DOMAINS}
    return records


def _empty_stats() -> dict[str, Any]:
    stats = {
        "total_records": 0,
        **{
            gender: {domain: 0 for domain in domains}
            for gender, domains in SUPPORTED_GENDER_DOMAINS.items()
        },
    }
    stats["shared"] = {domain: 0 for domain in SUPPORTED_SHARED_DOMAINS}
    return stats


def empty_line_bank_overrides(root: Path | None = None, *, enabled: bool = True) -> dict[str, Any]:
    return {
        "enabled": enabled,
        "root": str((root or LINE_BANK_ROOT).resolve()),
        "records": _empty_records(),
        "validation": {
            "warnings": [],
            "errors": [],
            "ignoredFiles": [],
            "stats": _empty_stats(),
        },
    }


def validate_line_bank_length(domain: str, value: str) -> str | None:
    spec = DOMAIN_SPECS[domain]
    if len(value) > int(spec["char_cap"]):
        return f"{domain} line exceeds {spec['char_cap']} chars"
    return None


def spicy_bucket_for_level(spicy_level: int | None) -> str | None:
    if spicy_level is None or spicy_level <= 0:
        return None
    if spicy_level <= 3:
        return "1_3"
    if spicy_level <= 5:
        return "4_5"
    return "6_8"


def records_for_level(
    payload: dict[str, Any],
    *,
    gender: str,
    domain: str,
    spicy_level: int | None,
) -> list[dict[str, Any]]:
    records = payload.get("records", {}).get(gender, {}).get(domain, [])
    if gender == "shared" and domain in SUPPORTED_SHARED_DOMAINS:
        return list(records)
    bucket = spicy_bucket_for_level(spicy_level)
    if bucket is None:
        return []
    return [record for record in records if record.get("line_bank_bucket") == bucket]


def shared_location_records_for_domain(
    payload: dict[str, Any],
    *,
    spicy_level: int | None,
    requested_location_domain: str,
) -> list[dict[str, Any]]:
    records = records_for_level(
        payload,
        gender="shared",
        domain="locations",
        spicy_level=spicy_level,
    )
    normalized_domain = str(requested_location_domain or "realism").strip().lower() or "realism"
    return [
        record
        for record in records
        if str(record.get("location_domain", "realism")).strip().lower() == normalized_domain
    ]


def _normalize_line(raw_line: str) -> str:
    return " ".join(raw_line.strip().split())


def _slugify(value: str) -> str:
    tokens = re.findall(r"[a-z0-9]+", value.lower())
    slug = "-".join(tokens[:10]).strip("-")
    return slug[:64] or "entry"


def _source_path(path: Path, root: Path) -> str:
    return f"overrides/{path.relative_to(root.parent).as_posix()}"


def _starter_key(value: str) -> str:
    tokens = re.findall(r"[a-z0-9]+", value.lower())
    return " ".join(tokens[:2])


@lru_cache(maxsize=4096)
def _infer_outfit_line_tags_cached(lowered: str) -> frozenset[str]:
    tags: set[str] = set()
    if any(token in lowered for token in ("tank", "shorts", "sundress", "sandals", "coverup", "sleeveless")):
        tags.add("hot_weather_ok")
    if any(token in lowered for token in ("blouse", "trousers", "knit", "midi skirt", "polo", "button shirt", "shirt")):
        tags.add("indoor_neutral_ok")
    if any(token in lowered for token in ("robe", "slip dress", "soft knit set", "lounge set", "lace set")):
        tags.add("lounge_ok")
    if any(token in lowered for token in ("bodysuit", "camisole", "bralette")):
        tags.add("body_reveal_like")
    if any(token in lowered for token in ("dress", "blouse", "tailored trousers", "midi skirt", "heels", "skirt")):
        tags.add("restaurant_ok")
    if any(token in lowered for token in ("leggings", "running shoes", "workout", "sport", "shorts", "zip jacket")):
        tags.add("active_ok")
    if any(
        token in lowered
        for token in (
            "workout",
            "training",
            "track",
            "running",
            "runner",
            "performance",
            "sports bra",
            "sports top",
            "tennis",
            "leggings",
            "zip jacket",
            "track jacket",
            "athletic",
            "active set",
        )
    ):
        tags.add("active_explicit")
    if any(token in lowered for token in ("bikini", "bra", "panties", "sheer", "open satin robe", "deep-cut", "lace set")):
        tags.add("minimal_coverage")
    if any(token in lowered for token in ("jacket", "cardigan", "coat", "overshirt", "blazer", "robe")):
        tags.add("layered_like")
    if any(token in lowered for token in ("satin", "tailored", "heels", "evening", "lace set", "midi skirt")):
        tags.add("dressy_like")
    if any(token in lowered for token in ("tee", "tank", "denim", "simple shirt", "casual", "sundress", "leggings", "running shoes")):
        tags.add("casual_like")
    if any(token in lowered for token in ("midi skirt", "trousers", "knit set", "soft skirt", "slip dress")):
        tags.add("seat_friendly")
    if re.search(r"\b(wet|damp|soaked|dripping)\b", lowered):
        tags.add("wet_like")
    if any(token in lowered for token in ("bathrobe", "robe")):
        tags.add("robe_like")
    if any(token in lowered for token in ("bikini", "swimsuit", "swimwear")):
        tags.add("swim_like")
    if any(token in lowered for token in ("latex", "vinyl")):
        tags.add("latex_like")
    if any(
        token in lowered
        for token in (
            "micro mini",
            "tiny pleated skirt",
            "tiny skirt",
            "short denim shorts",
            "low rise shorts",
            "hot shorts",
            "bandage style",
            "club mini dress",
            "racerback top",
            "spandex mini dress",
            "very short mini skirt",
        )
    ):
        tags.add("budget_club_like")
    if any(
        token in lowered
        for token in (
            "micro mini",
            "panties",
            "plunging neckline",
            "mesh top over",
            "deep-cut",
            "cutout",
            "low-draped",
            "open satin robe",
            "sheer dress",
            "bodysuit",
            "bralette",
            "camisole",
        )
    ):
        tags.add("public_risky")
    if any(
        token in lowered
        for token in (
            "lingerie",
            "lace set",
            "bra",
            "panties",
            "bare torso",
            "bare chest",
            "stockings",
            "thigh-high",
            "mesh top over",
            "sheer shirt over",
            "club bodysuit",
            "tiny lounge shorts",
            "opaque bodysuit",
            "camisole with tiny lounge shorts",
            "open black shirt over a bare torso",
            "open sheer shirt over a lean bare torso",
            "cropped leather jacket over a bare chest",
        )
    ):
        tags.add("intimate_like")
    if any(token in lowered for token in ("satin", "silk", "tailored", "trousers", "blouse", "dress", "polo")):
        tags.add("public_ok")
    return frozenset(tags)


def infer_outfit_line_tags(value: str) -> set[str]:
    lowered = str(value or "").strip().lower()
    return set(_infer_outfit_line_tags_cached(lowered))


@lru_cache(maxsize=4096)
def _infer_pose_line_tags_cached(lowered: str) -> frozenset[str]:
    tags: set[str] = set()
    if any(token in lowered for token in ("half-reclined", "reclined", "lying", "stretched out")):
        tags.add("lying_like")
    elif any(token in lowered for token in ("kneeling", "planted on the blanket", "planted on the bed", "anchored into the sheet", "anchored into the mattress")):
        tags.add("ground_low_like")
    elif any(token in lowered for token in ("sitting", "seated", "cross-legged", "chair back", "on the sofa", "on the edge of the bed", "on the edge of a chair")):
        tags.add("seated_like")
    else:
        tags.add("standing_like")

    if any(token in lowered for token in ("bed", "bedding", "blanket", "mattress", "sheet")):
        tags.add("bed_support")
    if any(token in lowered for token in ("chair", "stool", "chair back")):
        tags.add("chair_support")
    if any(token in lowered for token in ("sofa", "couch", "chaise", "banquette", "ottoman", "lounger", "daybed")):
        tags.add("sofa_support")
    if any(token in lowered for token in ("bench", "backrest")):
        tags.add("bench_support")
    if any(token in lowered for token in ("steps", "stair", "stairs")):
        tags.add("stairs_support")
    if any(token in lowered for token in ("mirror", "mirrored", "reflection")):
        tags.add("mirror_support")
    if any(token in lowered for token in ("sink", "basin", "washstand", "vanity")):
        tags.add("sink_support")
    if any(
        token in lowered
        for token in (
            "both arms lifted",
            "one arm raised",
            "braced overhead",
            "arms stretched above",
        )
    ):
        tags.add("overhead_arm_risk")
    return frozenset(tags)


def infer_pose_line_tags(value: str) -> set[str]:
    lowered = str(value or "").strip().lower()
    return set(_infer_pose_line_tags_cached(lowered))


@lru_cache(maxsize=4096)
def _infer_location_line_tags_cached(lowered: str) -> frozenset[str]:
    tags: set[str] = set()
    if any(
        token in lowered
        for token in (
            "rooftop",
            "terrace",
            "courtyard",
            "garden",
            "poolside",
            "boardwalk",
            "promenade",
            "marina",
            "cabana",
            "beach",
            "shore",
            "lawn",
            "meadow",
            "field",
            "park",
            "track",
            "stadium",
            "court",
            "trail",
        )
    ):
        tags.add("outdoor_like")
    else:
        tags.add("indoor_like")
    if any(token in lowered for token in ("hotel", "penthouse", "marble", "lounge", "lobby", "suite", "brass", "lacquer", "vanity")):
        tags.add("luxury_like")
    if any(token in lowered for token in ("cocktail", "bar", "neon", "booth", "after-dark", "nightclub", "club", "stage")):
        tags.add("nightlife_like")
    if any(token in lowered for token in ("poolside", "boardwalk", "marina", "cabana", "seaside", "coastal", "beach", "shore")):
        tags.add("coastal_like")
    if any(token in lowered for token in ("bookstore", "library", "reading", "shelf", "salon")):
        tags.add("bookish_like")
    if any(token in lowered for token in ("artist", "paint", "canvas", "gallery", "studio set", "projector")):
        tags.add("creative_like")
    if any(
        token in lowered
        for token in (
            "studio set",
            "theater backstage",
            "empty theater stage",
            "music venue backstage",
            "single spotlight",
            "velvet curtain",
        )
    ):
        tags.add("studio_practical_like")
    if any(token in lowered for token in ("spa", "vanity", "powder room", "dressing room", "bath")):
        tags.add("wellness_like")
    if any(
        token in lowered
        for token in (
            "cafe",
            "restaurant",
            "dining room",
            "terrace",
            "boardwalk",
            "street",
            "promenade",
            "bar",
            "lobby",
            "bridge",
            "aquarium",
            "tunnel",
        )
    ):
        tags.add("public_like")
    if any(
        token in lowered
        for token in (
            "private",
            "suite",
            "bedroom",
            "bathroom",
            "vanity",
            "dining room",
            "dressing",
            "closet",
            "apartment",
            "living room",
            "kitchen",
        )
    ):
        tags.add("private_like")
    if any(token in lowered for token in ("sunlit", "bright", "daylight", "midday", "morning", "afternoon", "golden-hour")):
        tags.add("day_capable")
    if any(token in lowered for token in ("dim", "night", "after-dark", "amber spill", "lamp glow", "evening", "cocktail", "neon")):
        tags.add("night_capable")
    if any(token in lowered for token in ("pool", "lagoon", "beach", "shore", "spa", "shower", "humid", "coastal", "marina", "cabana")):
        tags.add("wet_humid_like")
    if any(token in lowered for token in ("aquarium", "marine glow", "water shimmer", "curved blue glass")):
        tags.add("wet_humid_like")
    if any(token in lowered for token in ("pool", "infinity pool", "poolside", "lap pool")):
        tags.add("pool_like")
    if any(token in lowered for token in ("winter", "snow", "snowy", "alpine", "frost", "frosty", "ice", "icy", "glacier")):
        tags.add("winter_like")
    if any(token in lowered for token in ("chair", "chairs", "sofa", "banquette", "booth", "daybed", "bench", "lounger", "stool")):
        tags.add("seat_friendly")
    if any(token in lowered for token in ("hallway", "corridor", "walkway", "promenade", "street", "path", "steps", "stair landing", "landing")):
        tags.add("pass_through_like")
    if any(token in lowered for token in ("bedroom", "living room", "kitchen", "apartment", "balcony", "window seat", "closet", "suite")):
        tags.add("home_like")
    if any(token in lowered for token in ("cafe", "restaurant", "cocktail lounge", "terrace", "bar deck", "banquette")):
        tags.add("restaurant_like")
    if any(token in lowered for token in ("poolside", "marina", "cabana", "seaside", "boardwalk", "resort", "beach")):
        tags.add("resort_like")
    if any(token in lowered for token in ("school", "university", "classroom", "gym", "hallway", "corridor", "locker", "dorm")):
        tags.add("institutional_like")
    if any(token in lowered for token in ("train platform", "station", "tracks", "platform", "airport", "bus stop")):
        tags.add("transit_like")
    if any(token in lowered for token in ("record store", "shop", "store aisle", "boutique", "market stall")):
        tags.add("retail_like")
    if any(token in lowered for token in ("laboratory", "lab", "industrial", "metal tables", "floor mist", "factory", "warehouse")):
        tags.add("lab_industrial_like")
    if any(
        token in lowered
        for token in (
            "gym",
            "locker",
            "stadium",
            "track",
            "court",
            "training",
            "workout",
            "pilates",
            "yoga",
            "tennis",
            "ring edge",
            "running",
            "runner",
            "trail",
        )
    ):
        tags.add("active_like")
    if any(
        token in lowered
        for token in ("greenhouse", "conservatory", "garden", "courtyard", "lawn", "meadow", "field", "sunflower", "wildflower", "park")
    ):
        tags.add("garden_like")
    if any(token in lowered for token in ("city", "rooftop", "hotel", "lobby", "bridge", "office")):
        tags.add("urban_like")
    return frozenset(tags)


def infer_location_line_tags(value: str) -> set[str]:
    lowered = str(value or "").strip().lower()
    return set(_infer_location_line_tags_cached(lowered))


@lru_cache(maxsize=4096)
def _location_text_tokens(value: str) -> frozenset[str]:
    return frozenset(token for token in re.findall(r"[a-z0-9]+", str(value or "").lower()) if len(token) >= 3)


def line_bank_location_matches_exact_theme_keywords(record: dict[str, Any], exact_theme_keywords: set[str] | None = None) -> bool:
    keywords = {str(keyword).strip().lower() for keyword in (exact_theme_keywords or set()) if str(keyword).strip()}
    if not keywords:
        return True
    return bool(_location_text_tokens(record.get("value", "")) & keywords)


def line_bank_location_matches_requested_domain(
    record: dict[str, Any],
    requested_location_domain: str = "realism",
) -> bool:
    return str(record.get("location_domain", "realism")).strip().lower() == str(requested_location_domain or "realism").strip().lower()


def line_bank_outfit_matches_scene(
    record: dict[str, Any],
    *,
    scene_family_id: str,
    style_mode: str = "random",
    scene_tags: set[str] | None = None,
    setting_value: str = "",
) -> bool:
    scene_key = str(scene_family_id or "").strip().lower()
    lowered_setting = str(setting_value or "").strip().lower()
    lowered_outfit = str(record.get("value", "") or "").strip().lower()
    context_tags = {str(tag).strip().lower() for tag in (scene_tags or set())}
    scene_text_tags = infer_location_line_tags(lowered_setting)
    tags = set(record.get("tags", [])) | infer_outfit_line_tags(record.get("value", ""))
    active_context = style_mode in {"sport", "fitness"} or bool(
        context_tags & {"sporty", "active", "gym", "track", "stadium"}
        or scene_text_tags & {"active_like"}
    )
    publicish_context = bool(
        context_tags & {"public_elegant", "travel", "urban", "street", "dining"}
        or any(token in lowered_setting for token in ("corridor", "lounge", "lobby", "restaurant", "bar", "street", "dining room", "aquarium", "tunnel", "landing"))
    )
    if active_context:
        if "active_explicit" not in tags:
            return False
        if tags & {
            "swim_like",
            "dressy_like",
            "lounge_ok",
            "intimate_like",
            "public_risky",
            "body_reveal_like",
            "budget_club_like",
            "robe_like",
        }:
            return False
    if "swim_like" in tags and scene_key not in RESORT_SWIM_SCENES:
        return False
    if scene_key in RESORT_SWIM_SCENES and any(token in lowered_outfit for token in ("blazer", "leather jacket", "cropped jacket", "coat")):
        return False
    if "wet_like" in tags and scene_key not in WET_OUTFIT_CONTEXT_SCENES and not (context_tags & WET_OUTFIT_CONTEXT_TAGS):
        return False
    if "lab_industrial_like" in scene_text_tags:
        if tags & {"dressy_like", "lounge_ok", "intimate_like", "swim_like"}:
            return False
        if tags & {"minimal_coverage", "public_risky"} and style_mode not in {"studio", "creative_artistic", "fantasy", "cosplay"}:
            return False
    if "robe_like" in tags and (scene_key not in ROBE_OK_SCENES or publicish_context):
        return False
    if "latex_like" in tags and scene_key not in LATEX_OK_SCENES:
        return False
    if "intimate_like" in tags and (scene_key not in PRIVATE_OUTFIT_SCENES or publicish_context):
        return False
    if "body_reveal_like" in tags and "wet_humid_like" in scene_text_tags and "swim_like" not in tags and scene_key not in {"studio", "nightlife_neon"}:
        return False
    if "public_risky" in tags and scene_key not in PUBLIC_RISKY_OK_SCENES:
        return False
    if "public_risky" in tags and publicish_context and style_mode not in {"nightlife", "studio", "cosplay", "fantasy"}:
        return False
    if style_mode in {"lifestyle", "luxury", "old_money", "cultural_bookish", "urban_day"} and scene_key not in ROBE_OK_SCENES:
        if tags & {"swim_like", "robe_like", "public_risky"}:
            return False
    if "restaurant_ok" in tags and scene_key == "nightlife_bar" and "dressy_like" not in tags:
        return False
    if "active_ok" in tags and (context_tags & {"dining", "public_elegant"} or scene_key == "nightlife_bar"):
        return False
    if "active_like" in scene_text_tags:
        if scene_key not in {"urban_daylight", "wellness_spa", "coastal_boardwalk", "coastal_pool"}:
            return False
        if not (tags & {"active_explicit", "swim_like"}):
            return False
    if "lounge_ok" in tags and publicish_context and style_mode not in {"nightlife", "studio"}:
        return False
    if "pass_through_like" in scene_text_tags and tags & {"lounge_ok", "intimate_like"} and style_mode not in {"nightlife", "studio"}:
        return False
    if "minimal_coverage" in tags and publicish_context and style_mode not in {"nightlife", "studio", "coastal"}:
        return False
    if "budget_club_like" in tags and style_mode not in {"nightlife", "studio", "coastal", "creative_artistic"}:
        return False
    if "budget_club_like" in tags and scene_key in {"residential_luxury", "hospitality_suite", "culture_bookish", "garden_conservatory", "courtyard_garden"}:
        return False
    if "hot_weather_ok" in tags and scene_key in {"grooming_bath", "residential_luxury"} and "indoor_neutral_ok" not in tags:
        return False
    return True


def line_bank_pose_matches_scene(
    record: dict[str, Any],
    *,
    scene_family_id: str,
    scene_tags: set[str] | None = None,
    setting_value: str = "",
    framing_id: str = "",
) -> bool:
    scene_key = str(scene_family_id or "").strip().lower()
    lowered_setting = str(setting_value or "").strip().lower()
    context_tags = {str(tag).strip().lower() for tag in (scene_tags or set())}
    tags = set(record.get("tags", [])) | infer_pose_line_tags(record.get("value", ""))

    if "overhead_arm_risk" in tags and str(framing_id or "").strip().lower() in TIGHT_POSE_CROP_FRAMING_IDS:
        return False

    has_bed = "bedroom" in context_tags or any(token in lowered_setting for token in ("bed", "bedding", "headboard"))
    has_chair = any(token in lowered_setting for token in ("chair", "stool", "seat", "seating")) or bool(context_tags & {"lounge", "social"})
    has_sofa = any(token in lowered_setting for token in ("sofa", "couch", "banquette", "chaise", "ottoman", "lounger", "daybed"))
    has_bench = any(token in lowered_setting for token in ("bench", "backrest"))
    has_stairs = "stairs" in context_tags or any(token in lowered_setting for token in ("steps", "staircase", "stair hall", "stairs"))
    has_mirror = "mirror" in context_tags or any(token in lowered_setting for token in ("mirror", "mirrored", "reflection"))
    has_sink = "bathroom" in context_tags or any(token in lowered_setting for token in ("sink", "basin", "washstand", "vanity"))
    has_soft_ground = bool(context_tags & {"spa", "wellness", "coastal", "pool"}) or any(
        token in lowered_setting for token in ("grass", "sand", "lawn", "meadow", "mat", "blanket", "daybed", "lounger", "poolside")
    )
    public_hard_scene = bool(context_tags & {"public_elegant", "travel", "urban", "hotelized_living"}) or any(
        token in lowered_setting for token in ("corridor", "lobby", "bridge", "boardwalk", "street", "office", "path", "paving", "paved")
    )

    if "lying_like" in tags:
        return has_bed or has_sofa or has_soft_ground or scene_key == "studio"

    if "ground_low_like" in tags:
        return (has_bed or has_sofa or has_soft_ground or scene_key in {"grooming_bath", "studio"}) and not public_hard_scene

    if "bed_support" in tags and not has_bed:
        return False
    if "chair_support" in tags and not has_chair:
        return False
    if "sofa_support" in tags and not has_sofa:
        return False
    if "bench_support" in tags and not has_bench:
        return False
    if "stairs_support" in tags and not has_stairs:
        return False
    if "mirror_support" in tags and not has_mirror:
        return False
    if "sink_support" in tags and not has_sink:
        return False

    if "standing_like" in tags:
        return True

    if "seated_like" in tags:
        return has_bed or has_chair or has_sofa or has_bench or has_stairs

    return True


def line_bank_location_matches_scene(
    record: dict[str, Any],
    *,
    scene_family_id: str,
    scene_tags: set[str] | None = None,
    setting_value: str = "",
    exact_theme_keywords: set[str] | None = None,
    requested_location_domain: str = "realism",
) -> bool:
    scene_key = str(scene_family_id or "").strip().lower()
    lowered_setting = str(setting_value or "").strip().lower()
    context_tags = {str(tag).strip().lower() for tag in (scene_tags or set())}
    tags = set(record.get("tags", [])) | infer_location_line_tags(record.get("value", ""))
    active_context = bool(context_tags & {"sporty", "active", "gym", "track", "stadium"})

    if not line_bank_location_matches_requested_domain(record, requested_location_domain):
        return False

    if not line_bank_location_matches_exact_theme_keywords(record, exact_theme_keywords):
        return False

    if scene_key == "studio":
        return False

    if active_context:
        if tags & {
            "luxury_like",
            "nightlife_like",
            "bookish_like",
            "creative_like",
            "wellness_like",
            "restaurant_like",
            "institutional_like",
            "transit_like",
            "retail_like",
            "private_like",
            "home_like",
            "urban_like",
            "resort_like",
            "public_like",
            "pass_through_like",
        }:
            return False
        if not (tags & {"active_like", "garden_like", "coastal_like", "outdoor_like"}):
            return False

    if scene_key in {"hospitality_suite", "residential_luxury"} and tags & {"institutional_like", "transit_like", "retail_like", "nightlife_like", "creative_like"}:
        return False
    if scene_key in {"hospitality_suite", "residential_luxury"} and tags & {"wet_humid_like", "pool_like", "coastal_like", "resort_like"}:
        return False
    if scene_key == "culture_bookish" and tags & {"pool_like", "resort_like", "coastal_like"}:
        return False
    if "active_like" in tags and scene_key not in {"urban_daylight", "wellness_spa", "coastal_boardwalk", "coastal_pool"}:
        return False
    if scene_key == "garden_conservatory" and "garden_like" not in tags:
        return False
    if scene_key == "creative_gallery" and "creative_like" not in tags:
        return False
    if scene_key in {"nightlife_bar", "nightlife_neon"}:
        if "nightlife_like" not in tags and "night_capable" not in tags:
            return False
        if tags & {"coastal_like", "resort_like", "pool_like", "garden_like", "home_like", "transit_like"} and "nightlife_like" not in tags:
            return False
    if scene_key == "hospitality_suite" and not (tags & {"luxury_like", "private_like", "home_like"}):
        return False
    if scene_key == "residential_luxury" and not (tags & {"luxury_like", "private_like", "home_like"}):
        return False

    if "outdoor_like" in tags and "outdoor" not in context_tags and scene_key not in {"coastal_pool", "coastal_boardwalk", "courtyard_garden", "urban_daylight"}:
        return False
    if "indoor_like" in tags and "outdoor" in context_tags and "coastal_like" not in tags:
        return False
    if "nightlife_like" in tags and scene_key not in {"nightlife_bar", "nightlife_neon"}:
        return False
    if "coastal_like" in tags and scene_key not in {"coastal_pool", "coastal_boardwalk"}:
        return False
    if "bookish_like" in tags and scene_key != "culture_bookish":
        return False
    if "wellness_like" in tags and scene_key != "grooming_bath" and "spa" not in context_tags:
        return False
    if "restaurant_like" in tags and not (context_tags & {"dining", "social", "public_elegant"} or scene_key in {"urban_daylight", "nightlife_bar"}):
        return False
    if "private_like" in tags and context_tags & {"spa", "wellness"} and "wellness_like" not in tags:
        return False
    if "pass_through_like" in tags and context_tags & {"bedroom", "spa"}:
        return False
    if scene_key in {"urban_daylight", "coastal_pool", "coastal_boardwalk", "courtyard_garden", "garden_conservatory"}:
        if "night_capable" in tags and "day_capable" not in tags:
            return False
    if "winter_like" in tags and not any(token in lowered_setting for token in ("winter", "snow", "snowy", "alpine", "frost", "frosty", "ice", "icy", "glacier")):
        return False
    if "resort_like" in tags and scene_key not in {"coastal_pool", "coastal_boardwalk"}:
        return False
    if "garden_like" in tags and scene_key not in {"courtyard_garden", "garden_conservatory"}:
        return False
    return True


def normalize_line_bank_record(domain: str, bucket: str, value: str, path: Path, *, gender: str, root: Path | None = None) -> dict[str, Any]:
    spec = DOMAIN_SPECS[domain]
    is_shared_location_bank = domain == "locations" and gender == "shared" and bucket in SHARED_LOCATION_DOMAIN_BY_FILENAME
    if is_shared_location_bank:
        spicy_min, spicy_max = (1, 8)
    else:
        spicy_min, spicy_max = BUCKET_RANGES[bucket]
    digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:10]
    inferred_tags = infer_outfit_line_tags(value) if domain == "outfits" else set()
    if domain == "poses":
        inferred_tags = infer_pose_line_tags(value)
    if domain == "locations":
        inferred_tags = infer_location_line_tags(value)
    location_domain = SHARED_LOCATION_DOMAIN_BY_FILENAME.get(bucket, "realism") if is_shared_location_bank else "realism"
    return {
        "id": f"{spec['id_prefix']}__{gender}__{bucket}__{_slugify(value)}__{digest}",
        "value": value,
        "tags": [
            "line_bank",
            "user_override",
            str(spec["domain_tag"]),
            gender,
            f"spicy_{bucket}",
            *spec.get("extra_tags", []),
            f"location_domain_{location_domain}" if domain == "locations" else "",
            *sorted(inferred_tags),
        ],
        "weight": float(spec["weight"]),
        "status": "user_override",
        "source": _source_path(path, root or LINE_BANK_ROOT),
        "recommended_min_spicy": spicy_min,
        "recommended_max_spicy": spicy_max,
        "line_bank_gender": gender,
        "line_bank_domain": domain,
        "line_bank_bucket": bucket,
        "location_domain": location_domain,
    }


def parse_line_bank_file(path: Path, root: Path | None = None) -> dict[str, Any]:
    root = root or LINE_BANK_ROOT
    result = {
        "records": [],
        "warnings": [],
        "errors": [],
        "ignored": False,
    }
    try:
        relative = path.relative_to(root)
    except ValueError:
        result["errors"].append(f"Line-bank file sits outside root: {path}")
        return result

    if path.suffix.lower() != ".md":
        result["ignored"] = True
        return result

    parts = relative.parts
    if len(parts) != 3:
        result["ignored"] = True
        return result

    gender, domain, filename = parts
    bucket = path.stem.strip().lower()
    if gender in SUPPORTED_GENDER_DOMAINS:
        if domain not in SUPPORTED_GENDER_DOMAINS[gender]:
            result["errors"].append(f"Unsupported line-bank domain folder: {relative.as_posix()}")
            return result
    elif gender in SUPPORTED_SHARED_GROUPS:
        if domain not in SUPPORTED_SHARED_DOMAINS:
            result["errors"].append(f"Unsupported shared line-bank domain folder: {relative.as_posix()}")
            return result
    else:
        result["errors"].append(f"Unsupported line-bank gender folder: {relative.as_posix()}")
        return result
    is_shared_global = (
        gender in SUPPORTED_SHARED_GROUPS
        and domain in SHARED_GLOBAL_FILENAMES
        and bucket in SHARED_LOCATION_DOMAIN_BY_FILENAME
    )
    if bucket not in BUCKET_RANGES and not is_shared_global:
        result["errors"].append(f"Unsupported spicy bucket filename: {filename}")
        return result

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        result["errors"].append(f"Unreadable UTF-8 line-bank file: {_source_path(path, root)}")
        return result

    spec = DOMAIN_SPECS[domain]
    seen_values: set[str] = set()
    starter_counts: dict[str, int] = {}
    saw_non_comment_line = False
    for line_number, raw_line in enumerate(lines, start=1):
        normalized = _normalize_line(raw_line)
        if not normalized:
            continue
        if normalized.startswith("#"):
            continue

        saw_non_comment_line = True
        if len(normalized) < int(spec["min_chars"]):
            result["warnings"].append(
                f"{_source_path(path, root)}:{line_number} skipped short {domain} line"
            )
            continue

        length_issue = validate_line_bank_length(domain, normalized)
        if length_issue:
            result["errors"].append(
                f"{_source_path(path, root)}:{line_number} {length_issue}"
            )
            continue

        lowered = normalized.casefold()
        if lowered in seen_values:
            result["warnings"].append(
                f"{_source_path(path, root)}:{line_number} duplicate line skipped in same file"
            )
            continue
        seen_values.add(lowered)

        starter = _starter_key(normalized)
        if starter:
            starter_counts[starter] = starter_counts.get(starter, 0) + 1

        result["records"].append(
            normalize_line_bank_record(domain, bucket, normalized, path, gender=gender, root=root)
        )

    if not result["records"] and saw_non_comment_line:
        result["warnings"].append(f"{_source_path(path, root)} has no effective records")

    noisy_starters = sorted(starter for starter, count in starter_counts.items() if count >= 4)
    if noisy_starters:
        result["warnings"].append(
            f"{_source_path(path, root)} repeats the same starters too often: {', '.join(noisy_starters)}"
        )

    return result


def load_line_bank_overrides(root: Path | None = None) -> dict[str, Any]:
    root = root or LINE_BANK_ROOT
    payload = empty_line_bank_overrides(root)
    if not root.exists():
        return payload

    duplicate_value_sources: dict[tuple[str, str, str], list[str]] = {}
    seen_ids: set[str] = set()
    for path in sorted(root.rglob("*.md")):
        parsed = parse_line_bank_file(path, root=root)
        payload["validation"]["warnings"].extend(parsed["warnings"])
        payload["validation"]["errors"].extend(parsed["errors"])
        if parsed.get("ignored"):
            payload["validation"]["ignoredFiles"].append(str(path))
            continue

        for record in parsed["records"]:
            record_id = str(record["id"])
            if record_id in seen_ids:
                payload["validation"]["errors"].append(
                    f"Duplicate normalized line-bank id skipped: {record_id}"
                )
                continue
            seen_ids.add(record_id)

            gender = str(record["line_bank_gender"])
            domain = str(record["line_bank_domain"])
            source = str(record["source"])
            duplicate_key = (gender, domain, str(record["value"]).casefold())
            duplicate_value_sources.setdefault(duplicate_key, []).append(source)

            payload["records"][gender][domain].append(record)
            payload["validation"]["stats"][gender][domain] += 1
            payload["validation"]["stats"]["total_records"] += 1

    for (gender, domain, value), sources in sorted(duplicate_value_sources.items()):
        unique_sources = sorted(set(sources))
        if len(unique_sources) > 1:
            payload["validation"]["warnings"].append(
                f"Exact duplicate {domain} line across files for {gender}: {value[:80]}"
            )

    for gender, domains in SUPPORTED_GENDER_DOMAINS.items():
        for domain in domains:
            count = int(payload["validation"]["stats"][gender][domain])
            if count > DOMAIN_VOLUME_WARNING_THRESHOLD:
                payload["validation"]["warnings"].append(
                    f"{gender}/{domain} line-bank volume is high: {count} records"
                )
    for domain in SUPPORTED_SHARED_DOMAINS:
        count = int(payload["validation"]["stats"]["shared"][domain])
        if count > DOMAIN_VOLUME_WARNING_THRESHOLD:
            payload["validation"]["warnings"].append(
                f"shared/{domain} line-bank volume is high: {count} records"
            )

    return payload


def merge_line_bank_overrides(bank: dict[str, Any], *, enabled: bool = True) -> dict[str, Any]:
    merged = {**bank}
    merged["line_banks"] = load_line_bank_overrides() if enabled else empty_line_bank_overrides(enabled=False)
    return merged
