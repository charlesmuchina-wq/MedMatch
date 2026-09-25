"""
Unit tests for utils/metrics.py — the pure computation behind the recruitment
and DEI analytics endpoints.

These are DB-free and server-free (unlike the phase suites, which hit a running
backend), so they run anywhere:

    cd backend && python -m pytest tests/test_metrics_utils.py -v
    # or, without pytest installed:
    python backend/tests/test_metrics_utils.py
"""
import os
import sys

# Make the backend root importable whether run under pytest (rootdir=backend) or directly.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analytics_utils import (  # noqa: E402
    classify_status,
    tally_statuses,
    parse_dt,
    time_to_hire_days,
    average_time_to_hire,
    source_of,
    source_effectiveness,
    gender_parity_index,
    simpson_diversity_index,
    composite_dei_score,
)


# --- classify_status: the status-casing bug the old endpoint had ----------------

def test_classify_status_is_case_insensitive():
    for raw in ("Applied", "applied", "APPLIED", " Applied "):
        assert classify_status(raw) == "in_progress", raw
    for raw in ("Hired", "hired", "HIRED"):
        assert classify_status(raw) == "hired", raw
    for raw in ("Rejected", "rejected"):
        assert classify_status(raw) == "rejected", raw


def test_classify_status_across_vocabularies():
    # ATS intake + recruiter pipeline stages all count as in-progress.
    for raw in ("received", "new", "reviewing", "shortlisted",
                "interviewing", "Interview", "offered"):
        assert classify_status(raw) == "in_progress", raw
    assert classify_status(None) == "other"
    assert classify_status("") == "other"
    assert classify_status("archived") == "other"


def test_tally_statuses_merges_casing_and_classifies():
    counts = {"Applied": 3, "applied": 2, "received": 4, "hired": 1, "Rejected": 1}
    out = tally_statuses(counts)
    assert out["hired"] == 1
    assert out["rejected"] == 1
    assert out["in_progress"] == 3 + 2 + 4  # 9
    # "Applied" + "applied" merge into a single lowercased pipeline bucket.
    assert out["pipeline"]["applied"] == 5
    assert out["pipeline"]["received"] == 4
    assert out["pipeline"]["hired"] == 1


# --- parse_dt -------------------------------------------------------------------

def test_parse_dt_variants():
    assert parse_dt("2026-01-01T00:00:00Z").year == 2026
    assert parse_dt("2026-01-01T00:00:00+00:00") is not None
    assert parse_dt("2026-01-01") is not None          # date-only fallback
    naive = parse_dt("2026-01-01T00:00:00")            # naive -> assumed UTC
    assert naive is not None and naive.tzinfo is not None
    assert parse_dt("not-a-date") is None
    assert parse_dt(None) is None
    assert parse_dt("") is None


# --- time-to-hire ---------------------------------------------------------------

def test_time_to_hire_candidate_apply_path():
    # jobs.py path: applied_at + updated_at
    app = {"applied_at": "2026-01-01T00:00:00Z", "updated_at": "2026-01-15T00:00:00Z"}
    assert time_to_hire_days(app) == 14.0


def test_time_to_hire_ats_path():
    # ats.py path: applied_at + status_updated_at
    app = {"applied_at": "2026-01-01T00:00:00Z", "status_updated_at": "2026-01-11T00:00:00Z"}
    assert time_to_hire_days(app) == 10.0


def test_time_to_hire_missing_or_negative():
    assert time_to_hire_days({"applied_at": "2026-01-01T00:00:00Z"}) is None
    assert time_to_hire_days({"updated_at": "2026-01-01T00:00:00Z"}) is None
    # hire before apply -> discarded, not negative
    assert time_to_hire_days(
        {"applied_at": "2026-01-15T00:00:00Z", "updated_at": "2026-01-01T00:00:00Z"}
    ) is None


def test_average_time_to_hire():
    apps = [
        {"applied_at": "2026-01-01T00:00:00Z", "updated_at": "2026-01-15T00:00:00Z"},  # 14
        {"applied_at": "2026-01-01T00:00:00Z", "status_updated_at": "2026-01-11T00:00:00Z"},  # 10
        {"applied_at": "2026-01-01T00:00:00Z"},  # unusable -> ignored
    ]
    assert average_time_to_hire(apps) == 12.0
    assert average_time_to_hire([]) == 0.0


# --- source effectiveness -------------------------------------------------------

def test_source_of_prefers_top_level_then_nested():
    assert source_of({"source": "referral"}) == "referral"
    assert source_of({"job": {"source": "RemoteOK"}}) == "RemoteOK"
    assert source_of({}) == "unknown"


def test_source_effectiveness_percentages():
    apps = [
        {"source": "referral"}, {"source": "referral"},
        {"job": {"source": "job_board"}}, {"job": {"source": "job_board"}},
    ]
    eff = source_effectiveness(apps)
    assert eff == {"referral": 50, "job_board": 50}
    assert source_effectiveness([]) == {}


# --- DEI indices ----------------------------------------------------------------

def test_gender_parity_index():
    assert gender_parity_index({"Male": 50, "Female": 50}) == 1.0
    assert gender_parity_index({"male": 25, "female": 75}) == 0.33
    # Only unspecified data -> cannot judge.
    assert gender_parity_index({"Not specified": 40}) is None
    assert gender_parity_index({}) is None


def test_simpson_diversity_index():
    assert simpson_diversity_index({"A": 10, "B": 10}) == 0.5
    # Placeholder buckets are excluded.
    assert simpson_diversity_index({"A": 10, "B": 10, "Not specified": 100}) == 0.5
    # Fewer than two real categories -> None.
    assert simpson_diversity_index({"A": 10}) is None
    assert simpson_diversity_index({}) is None


def test_composite_dei_score():
    assert composite_dei_score(1.0, 0.5) == 75
    assert composite_dei_score(None, 0.5) == 50   # ignores None
    assert composite_dei_score(None, None) == 0


# --- standalone runner (no pytest required) -------------------------------------

if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {fn.__name__}: {e}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"ERROR {fn.__name__}: {type(e).__name__}: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    sys.exit(1 if failed else 0)
