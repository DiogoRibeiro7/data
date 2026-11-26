"""Inspect a manually downloaded October 2026 IMF WEO workbook offline."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

COUNTRIES = tuple(sorted("""AUT BEL BGR HRV CYP CZE DNK EST FIN FRA DEU GRC HUN
IRL ITA LVA LTU LUX MLT NLD POL PRT ROU SVK SVN ESP SWE USA GBR CHE JPN CHN IND
""".split()))
INDICATORS = ("NGDPD", "PPPGDP", "NGDP_RPCH")
EDITION = "October 2026"
SOURCE = "https://data.imf.org/Datasets/WEO"
TERMS = "https://www.imf.org/en/about/copyright-and-terms"
START, END, RELEASE_YEAR = 1995, 2031, 2026
REQUIRED = {
    "COUNTRY.ID", "INDICATOR.ID", "UNIT", "SCALE", "LATEST_ACTUAL_ANNUAL_DATA"
}
MISSING = {"", "--", "...", "N/A", "NA", "NAN", "NOT AVAILABLE"}


def cell_text(value: Any) -> str:
    """Return a trimmed text representation without changing missing values."""
    return "" if value is None else str(value).strip()


def year_value(value: Any) -> int | None:
    """Interpret integer-valued Excel year labels, rejecting arbitrary dates."""
    if isinstance(value, bool):
        return None
    try:
        year = float(cell_text(value))
    except ValueError:
        return None
    if not math.isfinite(year) or not year.is_integer() or not 1900 <= year <= 2200:
        return None
    return int(year)


def number(value: Any) -> float | None:
    """Parse a numeric observation; reject unknown textual missing markers."""
    if cell_text(value).upper() in MISSING:
        return None
    if isinstance(value, bool):
        raise ValueError("Boolean is not a WEO observation")
    result = float(cell_text(value).replace(",", ""))
    if not math.isfinite(result):
        raise ValueError(f"Nonfinite observation: {value!r}")
    return result


def observation_status(year: int, cutoff: int | None) -> str:
    """Preserve the IMF series-specific cutoff and distinguish future years."""
    if year > RELEASE_YEAR:
        return "projection"
    if cutoff is None:
        return "unknown_actual_status"
    if year <= cutoff:
        return "through_reported_actual_cutoff"
    return "estimate_or_projection"


def inspect_rows(rows: Iterable[tuple[Any, ...]]) -> dict[str, Any]:
    """Validate the Countries worksheet and report coverage without exporting values."""
    header: dict[str, int] | None = None
    years: dict[int, int] = {}
    seen: set[tuple[str, str]] = set()
    coverage: dict[str, Any] = {code: {} for code in INDICATORS}
    for index, row in enumerate(rows):
        if header is None:
            labels = [cell_text(cell).upper() for cell in row]
            if REQUIRED.issubset(labels):
                populated = [label for label in labels if label]
                if len(set(populated)) != len(populated):
                    raise ValueError("Duplicate nonblank workbook headers")
                header = {label: pos for pos, label in enumerate(labels) if label}
                years = {year: pos for pos, cell in enumerate(row)
                         if (year := year_value(cell)) is not None}
                if not set(range(START, END + 1)).issubset(years):
                    raise ValueError("Expected annual columns 1995–2031 are missing")
                if max(years) != END:
                    raise ValueError("Unexpected WEO projection horizon")
            elif index >= 19:
                raise ValueError("Could not find the documented WEO Countries schema")
            continue

        def get(label: str) -> Any:
            pos = header[label]
            return row[pos] if pos < len(row) else None

        country = cell_text(get("COUNTRY.ID")).upper()
        indicator = cell_text(get("INDICATOR.ID")).upper()
        if country not in COUNTRIES or indicator not in INDICATORS:
            continue
        key = (country, indicator)
        if key in seen:
            raise ValueError(f"Duplicate country/indicator: {key}")
        seen.add(key)
        raw_cutoff = get("LATEST_ACTUAL_ANNUAL_DATA")
        cutoff = year_value(raw_cutoff)
        if cutoff is None and cell_text(raw_cutoff).upper() not in MISSING:
            raise ValueError(f"Invalid actual-data cutoff: {key}")
        if cutoff is not None and cutoff > RELEASE_YEAR:
            raise ValueError(f"Actual-data cutoff exceeds release year: {key}")
        unit = cell_text(get("UNIT"))
        scale = cell_text(get("SCALE"))
        if not unit:
            raise ValueError(f"Missing observation unit: {key}")

        # Missing cells remain missing; no numerical GDP values enter the report.
        available: dict[str, list[int]] = {
            "through_reported_actual_cutoff": [],
            "estimate_or_projection": [],
            "projection": [],
            "unknown_actual_status": [],
            "missing": [],
        }
        for year in range(START, END + 1):
            pos = years[year]
            raw = row[pos] if pos < len(row) else None
            status = "missing" if number(raw) is None else observation_status(year, cutoff)
            available[status].append(year)
        coverage[indicator][country] = {
            "unit": unit, "scale": scale,
            "latest_actual_annual_data": cutoff, "years_by_status": available,
        }
    if header is None:
        raise ValueError("WEO header not found")
    if not all(coverage.values()):
        raise ValueError("One or more target indicator codes not found")
    absent = sorted([country, code] for country in COUNTRIES for code in INDICATORS
                    if (country, code) not in seen)
    return {
        "matched_series": len(seen),
        "expected_series": len(COUNTRIES) * len(INDICATORS),
        "absent_series": absent,
        "coverage": coverage,
    }


def inspect_workbook(workbook: Path) -> dict[str, Any]:
    """Read the local workbook with no network access and no raw data exports."""
    from openpyxl import load_workbook

    raw = workbook.read_bytes()
    book = load_workbook(workbook, read_only=True, data_only=True)
    try:
        if "Countries" not in book.sheetnames:
            raise ValueError("Expected Countries worksheet not present")
        result = inspect_rows(book["Countries"].iter_rows(values_only=True))
        return {
            "edition": EDITION,
            "edition_identity": "manually confirmed from IMF edition-specific download; horizon validated",
            "source_url": SOURCE,
            "terms_url": TERMS,
            "workbook_name": workbook.name,
            "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw),
            "inspected_at_utc": datetime.now(timezone.utc).isoformat(),
            "worksheets": book.sheetnames,
            "status": "metadata_only_pending_reuse_review",
            **result,
        }
    finally:
        book.close()


def main() -> None:
    """Require explicit edition confirmation and write a new local report."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--confirm-october-2026", action="store_true", required=True,
                        help="Confirm the workbook was obtained from the October 2026 IMF release.")
    args = parser.parse_args()
    result = inspect_workbook(args.workbook)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")


if __name__ == "__main__":
    main()
