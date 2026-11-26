"""Promote exactly the reviewed GDP-resilience candidate artifacts offline.

This module never fetches data, updates an existing snapshot, or pushes Git refs.
Run the registry generators and validation before committing its output.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml

SPECS = {
    "wdi": {
        "slug": "world-bank-wdi-gdp-resilience-2026-11-26",
        "manifest": "45807a39fe812ba771fb88812509cdd55c23b2f0cc020de799bde86cb2e1838f",
        "source_id": "2", "start": 1995, "end": 2025, "file_count": 24,
        "catalog": "https://datacatalog.worldbank.org/infrastructure-data/search/dataset/0037712/world-development-indicators",
        "title": "World Bank WDI: GDP, population and sectoral value added, 33 countries, 1995–2025",
        "vintage": "WDI source 2; observation lastupdated 2026-11-11",
        "coverage": "8,116 non-null of 8,184 requested cells; 68 explicit nulls. GDP and population complete. Broad sectors balanced through 2021 (1995–1996 also incomplete); manufacturing missing for Bulgaria. Manufacturing is nested within industry.",
    },
    "cwon": {
        "slug": "world-bank-cwon-2024-gdp-resilience-2026-11-26",
        "manifest": "9c64681577f4f4bf89f4e135ec05772bfb2712e8fcde52beaa8050be7145f6be",
        "source_id": "59", "start": 1995, "end": 2020, "file_count": 16,
        "catalog": "https://datacatalog.worldbank.org/search/dataset/0042066/wealth-accounting",
        "title": "World Bank CWON 2024: real wealth per capita and components, 33 requested countries, 1995–2020",
        "vintage": "Wealth Accounts source 59, lastupdated 2024-10-08; CWON 2024",
        "coverage": "5,821 non-null of 6,006 requested cells; 182 absent, three explicit nulls. Cyprus absent; Bulgaria 1995 total wealth, foreign assets and liabilities null. Bulgaria's 1996 total (192.0511 chained 2019 USD per capita) is an extreme baseline; report sensitivity without Bulgaria and with later starting years, never silently correct it.",
    },
}
SAFE_JSON = re.compile(r"[A-Za-z0-9._-]+\.json\Z")


def sha(raw: bytes) -> str:
    """Return SHA-256 of the exact byte string."""
    return hashlib.sha256(raw).hexdigest()


def verify_candidate(directory: Path, spec: dict[str, Any]) -> tuple[bytes, dict[str, Any], list[tuple[dict[str, Any], bytes]]]:
    """Validate manifest identity, file inventory and every source byte."""
    manifest_bytes = (directory / "manifest.json").read_bytes()
    if sha(manifest_bytes) != spec["manifest"]:
        raise ValueError("Candidate manifest differs from the independently reviewed artifact")
    manifest = json.loads(manifest_bytes)
    if (str(manifest["source_id"]) != spec["source_id"]
            or (manifest["start"], manifest["end"]) != (spec["start"], spec["end"])
            or len(set(manifest["countries"])) != 33
            or len(manifest["files"]) != spec["file_count"]
            or manifest["status"] != "candidate_only"):
        raise ValueError("Unexpected reviewed snapshot scope")
    records: list[tuple[dict[str, Any], bytes]] = []
    names: set[str] = set()
    for entry in manifest["files"]:
        filename = entry["path"]
        if (not isinstance(filename, str) or not SAFE_JSON.fullmatch(filename)
                or filename == "manifest.json" or filename in names):
            raise ValueError("Unsafe or duplicate manifest file name")
        names.add(filename)
        path = directory / filename
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"Missing or nonregular candidate file: {filename}")
        raw = path.read_bytes()
        if len(raw) != entry["bytes"] or sha(raw) != entry["sha256"]:
            raise ValueError(f"Candidate file does not match manifest: {filename}")
        records.append((entry, raw))
    if {p.name for p in directory.iterdir()} != names | {"manifest.json"}:
        raise ValueError("Unexpected candidate directory contents")
    return manifest_bytes, manifest, records


def promote(directory: Path, root: Path, key: str) -> None:
    """Stage a canonical package with explicit provenance and temporary adoption exemption."""
    spec = SPECS[key]
    manifest_bytes, manifest, records = verify_candidate(directory, spec)
    dataset = root / "datasets" / spec["slug"]
    if dataset.exists():
        raise FileExistsError(f"Refusing to replace existing dataset: {dataset}")
    policy_file = root / "reports" / "canonical-adoption-policy.json"
    policy = json.loads(policy_file.read_text(encoding="utf-8"))
    if any(item["dataset_id"] == spec["slug"] for item in policy["exemptions"]):
        raise ValueError("Unexpected existing adoption exemption")

    # Registry rejects duplicate raw byte hashes. Deduplicate the two identical
    # CWON source metadata responses; the untouched manifest records both.
    by_hash: dict[str, str] = {}
    aliases: dict[str, str] = {}
    raw_dir = dataset / "raw"
    raw_dir.mkdir(parents=True)
    files: list[dict[str, Any]] = []
    for entry, raw in records:
        filename = entry["path"]
        checksum = entry["sha256"]
        if checksum in by_hash:
            aliases[filename] = by_hash[checksum]
            continue
        by_hash[checksum] = filename
        (raw_dir / filename).write_bytes(raw)
        files.append({
            "path": f"raw/{filename}", "role": "raw", "format": "json",
            "encoding": "utf-8", "compression": None, "sha256": checksum,
            "notes": f"Unmodified API bytes; {entry['bytes']} bytes; retrieved {entry['retrieved_at']}; URL: {entry['url']}",
        })
    (raw_dir / "acquisition-manifest.json").write_bytes(manifest_bytes)
    files.append({
        "path": "raw/acquisition-manifest.json", "role": "raw", "format": "json",
        "encoding": "utf-8", "compression": None, "sha256": spec["manifest"],
        "notes": "Original acquisition provenance manifest (not an upstream observation response).",
    })
    dates = sorted(entry["retrieved_at"] for entry, _ in records)
    metadata = {
        "schema_version": 1, "id": spec["slug"], "title": spec["title"],
        "description": spec["coverage"] + " Original API responses and manifest.",
        "domain": ["economics", "national-accounts", "economic-growth", "wealth" if key == "cwon" else "population"],
        "source": {
            "publisher": "World Bank (and original providers identified in indicator metadata)",
            "url": spec["catalog"], "retrieved_at": "2026-11-26",
            "snapshot": f"{spec['vintage']}; API retrieval {dates[0]} to {dates[-1]}; manifest SHA-256 {spec['manifest']}",
        },
        "license": {
            "name": "CC BY 4.0 (World Bank dataset terms, including attribution and provider exceptions)",
            "url": spec["catalog"], "redistribution": "allowed",
        },
        "citation": {
            "text": f"World Bank. {'The Changing Wealth of Nations 2024' if key == 'cwon' else 'World Development Indicators'}. Retrieved November 26, 2026. Original provider attribution in raw metadata.",
            "url": spec["catalog"],
        },
        "files": sorted(files, key=lambda item: item["path"]), "lineage": [],
    }
    (dataset / "metadata.yaml").write_text(
        yaml.safe_dump(metadata, sort_keys=False, allow_unicode=True, width=100),
        encoding="utf-8",
    )
    alias_text = "\n".join(f"- `{name}` is byte-identical to stored `raw/{target}`; the manifest retains both retrievals." for name, target in sorted(aliases.items()))
    (dataset / "README.md").write_text(
        f"# {spec['title']}\n\n{spec['coverage']}\n\n"
        f"## Provenance\n\n{spec['vintage']}. Original [source catalog]({spec['catalog']}). "
        "All source bytes were checked against the reviewed manifest. "
        "The manifest is preserved unchanged. No missing data imputation.\n\n"
        f"{alias_text}\n\n"
        "## Usage and limitations\n\n"
        "See the [review and interpretation contract](../../docs/consumer-source-audits/reviewed-gdp-resilience-snapshots-2026-11-26.md). "
        "Retain World Bank and source-provider attribution; comply with the [dataset terms](https://data.worldbank.org/summary-terms-of-use). "
        "Do not add chained wealth components or treat missing observations as zero.\n",
        encoding="utf-8",
    )
    policy["exemptions"].append({
        "dataset_id": spec["slug"],
        "rationale": "Reviewed source promotion precedes the Medium-Blog GDP resilience analysis (PR #776). Remove when the implemented consumer registers its pinned registry revision, data paths and checksums.",
    })
    policy_file.write_text(json.dumps(policy, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    """Stage one or both independently reviewed candidate directories."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wdi", type=Path)
    parser.add_argument("--cwon", type=Path)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    if args.wdi is None and args.cwon is None:
        parser.error("Provide at least one reviewed candidate directory")
    for key in ("wdi", "cwon"):
        directory = getattr(args, key)
        if directory is not None:
            promote(directory, args.root, key)


if __name__ == "__main__":
    main()
