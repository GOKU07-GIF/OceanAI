from __future__ import annotations

import re
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

DEFAULT_TIMEZONE = "Asia/Kolkata"

_DAYPARTS: dict[str, tuple[time, time]] = {
    "morning": (time(6, 0), time(12, 0)),
    "afternoon": (time(12, 0), time(17, 0)),
    "evening": (time(17, 0), time(21, 0)),
    "night": (time(21, 0), time(23, 59, 59)),
}

_DAYPART_ALIASES = {
    "subah": "morning",
    "morning": "morning",
    "dopahar": "afternoon",
    "afternoon": "afternoon",
    "shaam": "evening",
    "sham": "evening",
    "evening": "evening",
    "raat": "night",
    "night": "night",
}


def _match_daypart(query: str) -> str | None:
    for raw, normalized in _DAYPART_ALIASES.items():
        if re.search(rf"\b{re.escape(raw)}\b", query):
            return normalized
    return None


def resolve_requested_time(
    query: str,
    *,
    now: datetime | None = None,
    timezone_name: str = DEFAULT_TIMEZONE,
) -> dict[str, str] | None:
    """Resolve common relative time phrases into an explicit local window.

    Supported examples include ``tomorrow morning``, ``kal subah``,
    ``today afternoon`` and a bare ``tomorrow``. Ambiguous phrases remain
    unresolved rather than being guessed.
    """
    tz = ZoneInfo(timezone_name)
    current = now.astimezone(tz) if now is not None else datetime.now(tz)
    normalized = " ".join(query.lower().split())

    is_tomorrow = bool(re.search(r"\b(tomorrow|kal)\b", normalized))
    is_today = bool(re.search(r"\b(today|aaj)\b", normalized))
    if not (is_tomorrow or is_today):
        return None

    target_date = current.date() + timedelta(days=1) if is_tomorrow else current.date()
    day_label = "tomorrow" if is_tomorrow else "today"

    daypart = _match_daypart(normalized)
    if daypart is None:
        start_local = datetime.combine(target_date, time.min, tzinfo=tz)
        end_local = datetime.combine(target_date, time(23, 59, 59), tzinfo=tz)
        label = day_label
    else:
        start_t, end_t = _DAYPARTS[daypart]
        start_local = datetime.combine(target_date, start_t, tzinfo=tz)
        end_local = datetime.combine(target_date, end_t, tzinfo=tz)
        label = f"{day_label} {daypart}"

    return {
        "label": label,
        "start": start_local.isoformat(timespec="seconds"),
        "end": end_local.isoformat(timespec="seconds"),
        "timezone": timezone_name,
        "resolution": "deterministic_relative_time",
    }
