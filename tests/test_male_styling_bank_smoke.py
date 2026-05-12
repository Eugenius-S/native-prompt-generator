import random

from backend import legacy_people


def test_random_male_outfit_uses_styling_bank_for_supported_style():
    outfit, vibe = legacy_people._choose_male_outfit(random.Random(7), "luxury", "random")
    assert vibe == "luxury"
    assert outfit in {
        "open-collar shirt with tailored trousers",
        "fine knit polo with tailored trousers",
        "black knit polo with sharp dark trousers",
        "lightweight blazer over a fine knit top with tailored trousers",
        "crisp fitted button-down worn slightly open at the collar with dark tailored trousers",
        "oversized tailored suit with relaxed drape and an open evening stance",
    }


def test_random_male_outfit_falls_back_for_uncovered_style():
    outfit, vibe = legacy_people._choose_male_outfit(random.Random(11), "fantasy", "random")
    assert vibe == "fantasy"
    assert outfit in {
        "cinematic fantasy tunic with fitted dark trousers",
        "layered hero-style shirt with a leather belt detail",
    }


def test_random_male_outfit_uses_broader_styling_bank_for_random_mode():
    outfits = {legacy_people._choose_male_outfit(random.Random(seed), "random", "random")[0] for seed in range(20)}

    assert "fitted t-shirt with relaxed trousers" not in outfits
    assert outfits <= {
        "open-collar shirt with tailored trousers",
        "fine knit polo with tailored trousers",
        "light overshirt over a fitted tee with relaxed trousers",
        "dark fitted shirt with slim trousers",
        "black knit polo with sharp dark trousers",
        "light linen shirt with pleated trousers",
        "lightweight blazer over a fine knit top with tailored trousers",
        "soft camp-collar shirt with relaxed pleated trousers",
        "washed tee under a relaxed blazer with tailored trousers",
        "soft linen shirt with relaxed pleated trousers",
        "fine knit crewneck sweater with dark tailored trousers",
        "crisp fitted button-down worn slightly open at the collar with dark tailored trousers",
    }
    assert len(outfits) >= 5


def test_coastal_male_outfit_bank_has_three_plus_variants():
    outfits = {legacy_people._choose_male_outfit(random.Random(seed), "coastal", "random")[0] for seed in range(20)}

    assert "soft camp-collar shirt with relaxed pleated trousers" in outfits
    assert "clean tailored swim shorts with a minimal resort-ready finish" in outfits
    assert len(outfits) >= 3
