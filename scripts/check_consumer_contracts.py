#!/usr/bin/env python3
"""Check active canonical consumer contracts for reachability and drift."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

import yaml

USER_AGENT = "DiogoRibeiro7-data-consumer-health/1.0"
TRANSIENT_HTTP = {408, 425, 429}
DRIFT_HTTP = {404, 410}


@dataclass(frozen=True)
class CheckResult:
    """One consumer contract health check."""

    consumer_id: str
    dataset_id: str
    check: str
    target: str
    status: str
    detail: str


def classify_http(code: int) -> tuple[str, str]:
    """Classify one HTTP status code."""

    if 200 <= code < 400:
        return "healthy", f"HTTP {code}"
    if code in DRIFT_HTTP:
        return "drift", f"HTTP {code}"
    if code in TRANSIENT_HTTP or code >= 500:
        return "warning", f"transient HTTP {code}"
    return "warning", f"unexpected HTTP {code}"


def default_opener(request: urllib.request.Request, timeout: float) -> int:
    """Perform a lightweight HTTP request and return the status code."""

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return int(response.status)
    except urllib.error.HTTPError as exc:
        return int(exc.code)


def request_url(
    url: str,
    *,
    opener: Callable[[urllib.request.Request, float], int],
    timeout: float,
) -> tuple[str, str]:
    """Check one URL and classify network failures conservatively."""

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/vnd.github+json,text/html;q=0.9,*/*;q=0.8",
        },
        method="GET",
    )
    try:
        code = opener(request, timeout)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return "warning", f"network error: {exc}"
    return classify_http(code)


def load_yaml(path: Path) -> dict[str, Any]:
    """Load one consumer record."""

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: metadata root must be a mapping")
    return raw


def github_commit_url(repository: str, commit: str) -> str:
    """Return the GitHub commit URL for a repository."""

    return f"https://github.com/{repository}/commit/{commit}"


def github_contents_url(repository: str, commit: str, path: str) -> str:
    """Return an immutable GitHub contents URL."""

    return f"https://github.com/{repository}/blob/{commit}/{path}"


def check_consumer_contracts(
    root: Path,
    *,
    opener: Callable[[urllib.request.Request, float], int] = default_opener,
    timeout: float = 20.0,
) -> list[CheckResult]:
    """Check active consumer relationship records against GitHub."""

    results: list[CheckResult] = []
    consumers_root = root / "consumers"
    if not consumers_root.is_dir():
        return results

    for consumer_dir in sorted(path for path in consumers_root.iterdir() if path.is_dir()):
        for record_path in sorted(consumer_dir.glob("*.yaml")):
            metadata = load_yaml(record_path)
            if metadata.get("status") != "active":
                continue

            consumer_id = str(metadata.get("consumer_id", ""))
            dataset_id = str(metadata.get("dataset_id", ""))
            repository = metadata.get("consumer_repository")
            consumer_commit = metadata.get("consumer_commit")
            registry_commit = metadata.get("registry_commit")
            canonical_path = metadata.get("path")
            evidence_url = metadata.get("evidence_url")

            if not isinstance(repository, str) or not repository:
                results.append(
                    CheckResult(
                        consumer_id,
                        dataset_id,
                        "consumer-repository",
                        str(record_path.relative_to(root)),
                        "drift",
                        "consumer_repository is missing",
                    )
                )
                continue

            repo_url = f"https://github.com/{repository}"
            status, detail = request_url(repo_url, opener=opener, timeout=timeout)
            results.append(
                CheckResult(
                    consumer_id,
                    dataset_id,
                    "consumer-repository",
                    repo_url,
                    status,
                    detail,
                )
            )

            if isinstance(consumer_commit, str) and consumer_commit:
                commit_url = github_commit_url(repository, consumer_commit)
                status, detail = request_url(
                    commit_url,
                    opener=opener,
                    timeout=timeout,
                )
                results.append(
                    CheckResult(
                        consumer_id,
                        dataset_id,
                        "consumer-commit",
                        commit_url,
                        status,
                        detail,
                    )
                )

            if isinstance(evidence_url, str) and evidence_url:
                status, detail = request_url(
                    evidence_url,
                    opener=opener,
                    timeout=timeout,
                )
                results.append(
                    CheckResult(
                        consumer_id,
                        dataset_id,
                        "evidence",
                        evidence_url,
                        status,
                        detail,
                    )
                )

            if isinstance(registry_commit, str) and isinstance(canonical_path, str):
                registry_target = github_contents_url(
                    "DiogoRibeiro7/data",
                    registry_commit,
                    canonical_path,
                )
                status, detail = request_url(
                    registry_target,
                    opener=opener,
                    timeout=timeout,
                )
                results.append(
                    CheckResult(
                        consumer_id,
                        dataset_id,
                        "registry-contract",
                        registry_target,
                        status,
                        detail,
                    )
                )

    return results


def report_payload(results: list[CheckResult]) -> dict[str, Any]:
    """Return machine-readable report payload."""

    counts = {"healthy": 0, "warning": 0, "drift": 0}
    for item in results:
        counts[item.status] += 1
    return {
        "schema_version": 1,
        "summary": counts,
        "results": [asdict(item) for item in results],
    }


def _markdown_cell(value: object) -> str:
    """Escape a Markdown table cell."""

    text = str(value).replace("\\", "\\\\")
    return text.replace("|", "\\|").replace("\n", "<br>")


def render_markdown(payload: dict[str, Any]) -> str:
    """Render the human-readable health report."""

    summary = payload["summary"]
    lines = [
        "# Consumer contract health report",
        "",
        f"- Healthy checks: **{summary['healthy']}**",
        f"- Transient warnings: **{summary['warning']}**",
        f"- Actionable drift: **{summary['drift']}**",
        "",
        "| Consumer | Dataset | Check | Status | Target | Detail |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in payload["results"]:
        lines.append(
            f"| {_markdown_cell(item['consumer_id'])} | "
            f"{_markdown_cell(item['dataset_id'])} | "
            f"{_markdown_cell(item['check'])} | "
            f"{_markdown_cell(item['status'])} | "
            f"{_markdown_cell(item['target'])} | "
            f"{_markdown_cell(item['detail'])} |"
        )
    lines.append("")
    lines.append(
        "Warnings represent transient or inconclusive network conditions and do not imply contract drift."
    )
    lines.append(
        "Drift requires human review; this checker never edits consumer records or downstream repositories."
    )
    lines.append("")
    return "\n".join(lines)


def write_reports(
    results: list[CheckResult],
    *,
    json_path: Path,
    markdown_path: Path,
) -> dict[str, Any]:
    """Write JSON and Markdown reports."""

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
    """Parse command-line arguments."""

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
        help="Return non-zero only when actionable consumer-contract drift exists.",
    )
    return parser.parse_args()


def main() -> int:
    """CLI entry point."""

    args = parse_args()
    try:
        results = check_consumer_contracts(
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
        "Consumer contract health: "
        f"{summary['healthy']} healthy, "
        f"{summary['warning']} warning(s), "
        f"{summary['drift']} drift finding(s)."
    )

    if args.fail_on_drift and summary["drift"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
