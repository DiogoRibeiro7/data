#!/usr/bin/env python3
"""Check external-source link health and detect actionable metadata drift."""

from __future__ import annotations

import argparse
import json
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

import yaml

USER_AGENT = "DiogoRibeiro7-data-registry-health/1.0"
TRANSIENT_HTTP = {408, 425, 429}
DRIFT_HTTP = {404, 410}


@dataclass(frozen=True)
class CheckResult:
    source_id: str
    check: str
    target: str
    status: str
    detail: str


def load_yaml(path: Path) -> dict[str, Any]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: metadata root must be a mapping")
    return raw


def load_catalog(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: catalog root must be an object")
    return raw


def classify_http(code: int) -> tuple[str, str]:
    if 200 <= code < 400:
        return "healthy", f"HTTP {code}"
    if code in DRIFT_HTTP:
        return "drift", f"HTTP {code}"
    if code in TRANSIENT_HTTP or 500 <= code < 600:
        return "warning", f"transient HTTP {code}"
    return "warning", f"unexpected HTTP {code}"


def request_url(
    url: str,
    *,
    opener: Callable[[urllib.request.Request, float], int] | None = None,
    timeout: float = 20.0,
) -> tuple[str, str]:
    """Return health classification for one URL.

    The optional opener exists for deterministic tests. It receives the
    prepared request and timeout and returns an HTTP status code.
    """

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "*/*",
        },
        method="GET",
    )

    try:
        if opener is not None:
            code = opener(request, timeout)
        else:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                code = int(response.status)
        return classify_http(code)
    except urllib.error.HTTPError as exc:
        return classify_http(int(exc.code))
    except (
        urllib.error.URLError,
        TimeoutError,
        socket.timeout,
        ConnectionError,
        OSError,
    ) as exc:
        return "warning", f"transient network error: {exc}"


def github_commit_url(source_url: str, commit: str) -> str | None:
    parsed = urllib.parse.urlparse(source_url)
    if parsed.netloc.lower() not in {"github.com", "www.github.com"}:
        return None
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2:
        return None
    owner, repository = parts[0], parts[1]
    if repository.endswith(".git"):
        repository = repository[:-4]
    return f"https://github.com/{owner}/{repository}/commit/{commit}"


def check_external_sources(
    root: Path,
    *,
    opener: Callable[[urllib.request.Request, float], int] | None = None,
    timeout: float = 20.0,
) -> list[CheckResult]:
    """Run deterministic structural checks plus live URL checks."""

    external_root = root / "external"
    catalog = load_catalog(external_root / "catalog.json")
    catalog_sources = catalog.get("sources")
    if not isinstance(catalog_sources, list):
        raise ValueError("external/catalog.json: sources must be a list")

    results: list[CheckResult] = []
    catalog_by_id: dict[str, dict[str, Any]] = {}
    for item in catalog_sources:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            results.append(
                CheckResult(
                    "<catalog>",
                    "catalog-entry",
                    "external/catalog.json",
                    "drift",
                    "catalog entry is missing a string id",
                )
            )
            continue
        source_id = item["id"]
        if source_id in catalog_by_id:
            results.append(
                CheckResult(
                    source_id,
                    "catalog-id",
                    "external/catalog.json",
                    "drift",
                    "duplicate source id in external catalog",
                )
            )
        catalog_by_id[source_id] = item

    metadata_ids: set[str] = set()
    for source_dir in sorted(path for path in external_root.iterdir() if path.is_dir()):
        metadata_path = source_dir / "metadata.yaml"
        if not metadata_path.is_file():
            continue

        metadata = load_yaml(metadata_path)
        source_id = metadata.get("id")
        if not isinstance(source_id, str) or not source_id:
            results.append(
                CheckResult(
                    source_dir.name,
                    "metadata-id",
                    str(metadata_path.relative_to(root)),
                    "drift",
                    "metadata id is missing",
                )
            )
            continue

        metadata_ids.add(source_id)
        if source_id != source_dir.name:
            results.append(
                CheckResult(
                    source_id,
                    "metadata-id",
                    str(metadata_path.relative_to(root)),
                    "drift",
                    f"id does not match directory name {source_dir.name!r}",
                )
            )

        catalog_entry = catalog_by_id.get(source_id)
        if catalog_entry is None:
            results.append(
                CheckResult(
                    source_id,
                    "catalog-membership",
                    "external/catalog.json",
                    "drift",
                    "metadata id is missing from generated catalog",
                )
            )
        elif catalog_entry.get("path") != f"external/{source_id}":
            results.append(
                CheckResult(
                    source_id,
                    "catalog-path",
                    "external/catalog.json",
                    "drift",
                    "catalog path does not match metadata id",
                )
            )

        source_url = metadata.get("source_url")
        availability = metadata.get("availability")
        availability_state = "live"
        replacement_url: str | None = None
        if isinstance(availability, dict):
            state = availability.get("state")
            if isinstance(state, str) and state:
                availability_state = state
            candidate = availability.get("replacement_url")
            if isinstance(candidate, str) and candidate:
                replacement_url = candidate

        terminal_state = availability_state in {
            "permanently-unavailable",
            "legal-withdrawal",
        }
        moved_state = availability_state == "moved"

        if terminal_state:
            results.append(
                CheckResult(
                    source_id,
                    "availability-state",
                    str(source_url or ""),
                    "tombstone",
                    f"committed terminal state: {availability_state}",
                )
            )
        elif moved_state:
            results.append(
                CheckResult(
                    source_id,
                    "availability-state",
                    str(source_url or ""),
                    "moved",
                    "authoritative source has a committed replacement endpoint",
                )
            )
            if replacement_url is not None:
                status, detail = request_url(
                    replacement_url,
                    opener=opener,
                    timeout=timeout,
                )
                results.append(
                    CheckResult(
                        source_id,
                        "replacement-url",
                        replacement_url,
                        status,
                        detail,
                    )
                )
        elif isinstance(source_url, str) and source_url:
            status, detail = request_url(source_url, opener=opener, timeout=timeout)
            results.append(
                CheckResult(source_id, "source-url", source_url, status, detail)
            )

        if terminal_state:
            continue

        license_data = metadata.get("license")
        if isinstance(license_data, dict):
            license_url = license_data.get("url")
            if isinstance(license_url, str) and license_url:
                status, detail = request_url(
                    license_url, opener=opener, timeout=timeout
                )
                results.append(
                    CheckResult(
                        source_id, "license-url", license_url, status, detail
                    )
                )

        doi = metadata.get("doi")
        if isinstance(doi, str) and doi:
            doi_url = f"https://doi.org/{doi}"
            status, detail = request_url(doi_url, opener=opener, timeout=timeout)
            results.append(CheckResult(source_id, "doi", doi_url, status, detail))

        commit = metadata.get("source_commit")
        if isinstance(commit, str) and commit and not moved_state:
            commit_url = github_commit_url(str(source_url), commit)
            if commit_url is None:
                results.append(
                    CheckResult(
                        source_id,
                        "pinned-commit",
                        commit,
                        "drift",
                        "source_commit is present but source_url is not a GitHub repository URL",
                    )
                )
            else:
                status, detail = request_url(
                    commit_url, opener=opener, timeout=timeout
                )
                results.append(
                    CheckResult(
                        source_id, "pinned-commit", commit_url, status, detail
                    )
                )

    for source_id in sorted(set(catalog_by_id) - metadata_ids):
        results.append(
            CheckResult(
                source_id,
                "catalog-membership",
                "external/catalog.json",
                "drift",
                "catalog id has no matching external metadata directory",
            )
        )

    return results


def report_payload(results: list[CheckResult]) -> dict[str, Any]:
    counts = {
        "healthy": 0,
        "warning": 0,
        "drift": 0,
        "moved": 0,
        "tombstone": 0,
    }
    for item in results:
        counts[item.status] = counts.get(item.status, 0) + 1
    return {
        "schema_version": 1,
        "summary": counts,
        "results": [asdict(item) for item in results],
    }


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# External source health report",
        "",
        f"- Healthy checks: **{summary['healthy']}**",
        f"- Transient warnings: **{summary['warning']}**",
        f"- Actionable drift: **{summary['drift']}**",
        f"- Moved sources: **{summary['moved']}**",
        f"- Terminal tombstones: **{summary['tombstone']}**",
        "",
        "| Source | Check | Status | Target | Detail |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in payload["results"]:
        target = str(item["target"]).replace("|", "\\|")
        detail = str(item["detail"]).replace("|", "\\|")
        lines.append(
            f"| {item['source_id']} | {item['check']} | {item['status']} | "
            f"{target} | {detail} |"
        )
    lines.append("")
    lines.append(
        "Warnings represent transient/unconfirmed network conditions and do not imply metadata changes."
    )
    lines.append(
        "Drift requires human review; this checker never edits provenance, licensing, or source metadata."
    )
    lines.append(
        "Moved and tombstone states come only from reviewed committed metadata and are not inferred from one network observation."
    )
    lines.append("")
    return "\n".join(lines)


def write_reports(
    results: list[CheckResult],
    *,
    json_path: Path,
    markdown_path: Path,
) -> dict[str, Any]:
    payload = report_payload(results)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    markdown_path.write_text(render_markdown(payload), encoding="utf-8")
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument("--json-report", type=Path, required=True)
    parser.add_argument("--markdown-report", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument(
        "--fail-on-drift",
        action="store_true",
        help="Return non-zero only when confirmed structural/actionable drift exists.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        results = check_external_sources(
            args.root.resolve(),
            timeout=args.timeout,
        )
        payload = write_reports(
            results,
            json_path=args.json_report,
            markdown_path=args.markdown_report,
        )
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    summary = payload["summary"]
    print(
        "External source health: "
        f"{summary['healthy']} healthy, "
        f"{summary['warning']} warning(s), "
        f"{summary['drift']} drift finding(s), "
        f"{summary['moved']} moved, "
        f"{summary['tombstone']} tombstone(s)."
    )

    if args.fail_on_drift and summary["drift"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
