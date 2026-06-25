import json
import os
from pathlib import Path

from api.services.cbr_core import ExportCase, build_case

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CASES_DIR = str(PROJECT_ROOT / "data" / "cases")

_cache: list[ExportCase] | None = None


def load_all_cases() -> list[ExportCase]:
    global _cache
    if _cache is not None:
        return _cache

    cases = []
    if not os.path.isdir(CASES_DIR):
        print(f"Warning: cases directory not found at {CASES_DIR}", file=__import__("sys").stderr)
        _cache = []
        return _cache

    for filename in sorted(os.listdir(CASES_DIR)):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(CASES_DIR, filename)
        try:
            with open(filepath) as f:
                data = json.load(f)
            case = build_case(data)
            cases.append(case)
        except Exception as e:
            print(f"Error loading {filename}: {e}", file=__import__("sys").stderr)

    _cache = cases
    return cases


def get_case_count() -> int:
    return len(load_all_cases())


def add_case(case: ExportCase):
    cases = load_all_cases()
    cases.append(case)


def search_cases(
    query: ExportCase | None = None,
    status_filter: str | None = None,
    limit: int = 50,
) -> list[ExportCase]:
    cases = load_all_cases()
    if status_filter:
        cases = [c for c in cases if c.outcome == status_filter]
    if limit:
        cases = cases[:limit]
    return cases
