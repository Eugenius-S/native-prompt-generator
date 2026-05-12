from __future__ import annotations

from typing import Any

from . import legacy_people as _legacy_people


def preview_male_identities(*args: Any, **kwargs: Any):
    return _legacy_people.preview_male_identities(*args, **kwargs)


def render_batch(*args: Any, **kwargs: Any):
    return _legacy_people.render_batch(*args, **kwargs)
