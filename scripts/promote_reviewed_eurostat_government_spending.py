"""Register only the reviewed 28 November Eurostat artifact, without new downloads."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

import yaml

SLUG = "eurostat-government-spending-gdp-2026-11-28"
MANIFEST_SHA = "464eabbea0850dfa7d0114901286181fb64f94631cc6bb526b74725915979842"
SOURCE_FILES = {
    "fiscal.json": ("79b09a14b89cf193b4d228e7d598a81389e041e3f8b3ff85a3efe56e3e16addb", 110701, 9203),
    "growth.json": ("86872573b552ba3cdb4ea4b61b3032fdd31bc3ac78a7b6ded8edbeccb8b3c463", 12642, 809),
    "nominal_gdp.json": ("2b6fe8c0aa069974f13cf582c34755d4227397638123b4cc7fe8d597b3be9a16", 16643, 837),
}
TITLE = "Eurostat: government expenditure, value added and GDP, EU27, 1995–2025"
POLICY = "https://ec.europa.eu/eurostat/help/copyright-notice"
CATALOG = "https://ec.europa.eu/eurostat/databrowser/view/gov_10a_main/default/table?lang=en"
DESCRIPTION = (
    "11 fiscal series for S13 in percent of GDP, nominal GDP in EUR millions and annual real GDP growth. "
    "Fixed EU27 membership, 1995–2025; 10,849 non-null of 10,881 cells. "
    "32 missing cells; 58 provisional flags and 29 time-series break flags."
)


def digest(raw: bytes) -> str:
    """Return an exact-byte SHA-256 digest."""
    return hashlib.sha256(raw).hexdigest()


def verify_candidate(candidate: Path) -> dict[str, Any]:
    """Fail closed on any change to the independently audited manifest or data."""
    manifest_bytes = (candidate / "manifest.json").read_bytes()
    if digest(manifest_bytes) != MANIFEST_SHA:
        raise ValueError("Not the reviewed Eurostat manifest")
    manifest = json.loads(manifest_bytes)
    entries = manifest["files"]
    if len(entries) != len(SOURCE_FILES) or {e["path"] for e in entries} != set(SOURCE_FILES):
        raise ValueError("Unexpected manifest files")
    if {p.name for p in candidate.iterdir()} != set(SOURCE_FILES) | {"manifest.json"}:
        raise ValueError("Unexpected candidate directory entries")
    for entry in entries:
        name = entry["path"]
        expected_hash, size, count = SOURCE_FILES[name]
        data = (candidate / name).read_bytes()
        if (digest(data), len(data)) != (expected_hash, size):
            raise ValueError(f"Reviewed bytes differ: {name}")
        if (entry["sha256"], entry["bytes"], entry["non_null_observations"]) != (expected_hash, size, count):
            raise ValueError(f"Reviewed manifest metadata differs: {name}")
        payload = json.loads(data)
        if payload["source"] != "ESTAT" or payload["class"] != "dataset":
            raise ValueError(f"Unexpected publisher or format: {name}")
        if sum(v is not None for v in payload["value"].values()) != count:
            raise ValueError(f"Unexpected observation count: {name}")
    return manifest


def stage(candidate: Path, root: Path) -> None:
    """Copy the exact bytes, write canonical metadata and record adoption exemption."""
    manifest = verify_candidate(candidate)
    target = root / "datasets" / SLUG
    policy_path = root / "reports" / "canonical-adoption-policy.json"
    adoption = json.loads(policy_path.read_text(encoding="utf-8"))
    if target.exists() or any(x["dataset_id"] == SLUG for x in adoption["exemptions"]):
        raise ValueError("Snapshot or exemption already exists; refusing overwrite")
    raw_dir = target / "raw"
    raw_dir.mkdir(parents=True, exist_ok=False)
    files = []
    for entry in manifest["files"]:
        name = entry["path"]
        shutil.copyfile(candidate / name, raw_dir / name)
        files.append({
            "path": f"raw/{name}", "role": "raw", "format": "json", "encoding": "utf-8",
            "compression": None, "sha256": entry["sha256"],
            "notes": f"Exact Eurostat JSON-stat response; {entry['bytes']} bytes; "
                     f"retrieved {entry['retrieved_utc']}; updated {entry['source_updated']}; URL: {entry['url']}",
        })
    shutil.copyfile(candidate / "manifest.json", raw_dir / "manifest.json")
    files.append({"path": "raw/manifest.json", "role": "raw", "format": "json",
                  "encoding": "utf-8", "compression": None, "sha256": MANIFEST_SHA,
                  "notes": "Original acquisition manifest, not an observation response."})
    metadata = {
        "schema_version": 1, "id": SLUG, "title": TITLE, "description": DESCRIPTION,
        "domain": ["economics", "national-accounts", "public-finance", "economic-growth"],
        "source": {"publisher": "Eurostat", "url": CATALOG, "retrieved_at": "2026-11-28",
                   "snapshot": f"gov_10a_main updated 2026-10-21; nama_10_gdp updated 2026-11-27; manifest SHA-256 {MANIFEST_SHA}"},
        "license": {"name": "Eurostat statistical data reuse policy (attribution required)",
                    "url": POLICY, "redistribution": "allowed"},
        "citation": {"text": "Eurostat, gov_10a_main (10.2908/GOV_10A_MAIN) and nama_10_gdp "
                             "(10.2908/NAMA_10_GDP), customised EU27 extracts, accessed 2026-11-28.",
                     "url": CATALOG},
        "files": files, "lineage": [],
    }
    (target / "metadata.yaml").write_text(yaml.safe_dump(metadata, sort_keys=False, allow_unicode=True), encoding="utf-8")
    (target / "README.md").write_text(
        f"# {TITLE}\n\n{DESCRIPTION}\n\n"
        "## Provenance and interpretation\n\n"
        "Source: [gov_10a_main](https://doi.org/10.2908/GOV_10A_MAIN) and "
        "[nama_10_gdp](https://doi.org/10.2908/NAMA_10_GDP), Eurostat, accessed 2026-11-28. "
        "Original data and quality flags preserved unchanged. "
        "See the [independent audit](../../docs/consumer-source-audits/eurostat-government-spending-2026-11-28.md). "
        "Government expenditure is not government value added. S13 excludes public corporations outside general government; "
        "do not interpret the residual as exclusively private production. GDP series and fiscal series have different update dates. "
        "Attribute Eurostat, identify modifications, and state that Eurostat is not responsible for derived analysis. "
        f"[Reuse conditions]({POLICY}).\n", encoding="utf-8")
    adoption["exemptions"].append({"dataset_id": SLUG, "rationale":
        "Reviewed source promotion precedes the final pinned Medium-Blog government spending analysis (PR #794). "
        "Remove when the implemented consumer registers the merged registry revision, source paths and all hashes."})
    policy_path.write_text(json.dumps(adoption, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    """Stage an independently reviewed candidate into the registry checkout."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    stage(args.candidate, args.root)


if __name__ == "__main__":
    main()
