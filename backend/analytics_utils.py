"""
Pure, dependency-free helpers for recruitment & DEI analytics.

Extracted from the route handlers so the computation is unit-testable without a
running server or database. Every function here takes plain dicts/lists (already
fetched from Mongo) and returns computed values — no FastAPI, Motor, or `server`
imports, so `tests/test_metrics_utils.py` can exercise them directly.

Background: the `applications` collection is written by several code paths with
inconsistent status casing and two different vocabularies:
  - candidate self-apply (routes/jobs.py):   status "Applied", ts applied_at/updated_at,
                                              source nested under `job.source`
  - ATS intake (routes/ats.py):              status "received", ts applied_at/status_updated_at,
                                              top-level `source`
  - recruiter pipeline (routes/recruiter.py): new/reviewing/shortlisted/interviewing/
                                              offered/rejected/hired
Classification is therefore case-insensitive and vocabulary-tolerant, and the
timestamp/source helpers look across all the field names the write paths use.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable, Optional


# --- Application status taxonomy -------------------------------------------------

_HIRED = {"hired", "accepted", "admitted", "placed"}
_REJECTED = {"rejected", "declined", "denied", "withdrawn"}
# Open/active application stages across all vocabularies:
_IN_PROGRESS = {
    "applied", "received", "new", "open", "reviewing", "review", "in_review",
    "in review", "screening", "shortlisted", "interview", "interviewing",
    "offered", "offer", "pending", "pending_review", "submitted",
}


def classify_status(status: Optional[str]) -> str:
    """Map a raw application status to 'hired' | 'rejected' | 'in_progress' |
    'other' (case-insensitive, so "Applied"/"applied"/"APPLIED" all match)."""
    if not status:
        return "other"
    s = str(status).strip().lower()
    if s in _HIRED:
        return "hired"
    if s in _REJECTED:
        return "rejected"
    if s in _IN_PROGRESS:
        return "in_progress"
    return "other"


def tally_statuses(counts_by_raw_status: dict) -> dict:
    """Given ``{raw_status: count}`` (e.g. from a Mongo ``$group``), return
    classified totals plus a normalized pipeline breakdown where casing variants
    are merged. Returns ``{hired, rejected, in_progress, pipeline{status: count}}``."""
    hired = rejected = in_progress = 0
    pipeline: dict = {}
    for raw, count in (counts_by_raw_status or {}).items():
        c = int(count or 0)
        key = (str(raw).strip().lower() if raw else "unknown") or "unknown"
        pipeline[key] = pipeline.get(key, 0) + c
        klass = classify_status(raw)
        if klass == "hired":
            hired += c
        elif klass == "rejected":
            rejected += c
        elif klass == "in_progress":
            in_progress += c
    return {
        "hired": hired,
        "rejected": rejected,
        "in_progress": in_progress,
        "pipeline": pipeline,
    }


# --- Datetime parsing ------------------------------------------------------------

def parse_dt(value: Any) -> Optional[datetime]:
    """Parse an ISO-8601 string (or pass through a datetime) to an aware
    datetime, tolerating a trailing 'Z' and falling back to a date-only value.
    Returns None if unparseable."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        try:
            dt = datetime.strptime(text[:10], "%Y-%m-%d")
        except ValueError:
            return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


# Timestamp field names used by the different write paths (earliest-wins order).
_APPLY_FIELDS = ("applied_at", "created_at", "submitted_at")
_HIRE_FIELDS = ("hired_at", "status_updated_at", "updated_at")


def time_to_hire_days(app: dict) -> Optional[float]:
    """Days between application and hire for one application dict. Uses the first
    available apply timestamp and the first available hire timestamp. Returns
    None if either is missing or the result is negative (clock skew / bad data)."""
    apply_dt = next((parse_dt(app.get(f)) for f in _APPLY_FIELDS if app.get(f)), None)
    hire_dt = next((parse_dt(app.get(f)) for f in _HIRE_FIELDS if app.get(f)), None)
    if not apply_dt or not hire_dt:
        return None
    delta_days = (hire_dt - apply_dt).total_seconds() / 86400.0
    if delta_days < 0:
        return None
    return delta_days


def average_time_to_hire(hired_apps: Iterable[dict]) -> float:
    """Average time-to-hire in days across hired applications (rounded to 1dp).
    Returns 0.0 when there is no usable timestamp data."""
    durations = [d for d in (time_to_hire_days(a) for a in hired_apps) if d is not None]
    if not durations:
        return 0.0
    return round(sum(durations) / len(durations), 1)


# --- Source effectiveness --------------------------------------------------------

def source_of(app: dict) -> str:
    """Best-effort source of an application: top-level ``source`` wins, then the
    nested ``job.source`` (candidate-apply path), else 'unknown'."""
    src = app.get("source")
    if not src:
        job = app.get("job")
        if isinstance(job, dict):
            src = job.get("source")
    return str(src).strip() if src else "unknown"


def source_effectiveness(apps: Iterable[dict]) -> dict:
    """Return ``{source: percent}`` shares (integers), highest first. Percentages
    because the UI renders each as a ``{pct}%`` bar. Empty input -> ``{}``."""
    counts: dict = {}
    total = 0
    for app in apps:
        s = source_of(app)
        counts[s] = counts.get(s, 0) + 1
        total += 1
    if total == 0:
        return {}
    ordered = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    return {s: round(c / total * 100) for s, c in ordered}


# --- DEI indices -----------------------------------------------------------------

_MALE = {"male", "man", "m", "men"}
_FEMALE = {"female", "woman", "f", "women"}


def gender_parity_index(gender_dist: dict) -> Optional[float]:
    """Parity between the male and female buckets as ``min/max`` in [0, 1]
    (1.0 = perfect balance). Ignores 'Not specified'/other buckets and is
    case-insensitive. Returns None when there is no gendered data to judge."""
    male = female = 0
    for key, count in (gender_dist or {}).items():
        k = str(key).strip().lower()
        if k in _MALE:
            male += int(count or 0)
        elif k in _FEMALE:
            female += int(count or 0)
    hi = max(male, female)
    if hi == 0:
        return None
    return round(min(male, female) / hi, 2)


def simpson_diversity_index(
    dist: dict, exclude: Iterable[str] = ("not specified", "unknown", "")
) -> Optional[float]:
    """Gini-Simpson diversity index ``1 - sum(p_i^2)`` in [0, 1); higher = more
    evenly spread across categories. Excludes placeholder buckets. Returns None
    if fewer than two categories have data."""
    excl = {str(e).strip().lower() for e in exclude}
    counts = [
        int(v or 0)
        for k, v in (dist or {}).items()
        if str(k).strip().lower() not in excl and int(v or 0) > 0
    ]
    total = sum(counts)
    if total == 0 or len(counts) < 2:
        return None
    return round(1 - sum((c / total) ** 2 for c in counts), 2)


def composite_dei_score(*indices: Optional[float]) -> int:
    """Blend the available indices (each 0..1) into a 0..100 score, ignoring
    None values. Returns 0 when no index is available."""
    vals = [i for i in indices if i is not None]
    if not vals:
        return 0
    return round(sum(vals) / len(vals) * 100)
