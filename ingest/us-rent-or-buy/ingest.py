"""Temporary ingestion run for the US rent-or-buy sources (removed once the records are written).

Public-domain series are saved byte for byte under datasets/<id>/raw/; third-party copyrighted
files are only downloaded to measure them, and their URL, size and SHA-256 go to manifest.tsv.
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
UA = "Mozilla/5.0 (X11; Linux x86_64) research-download (dfr@esmad.ipp.pt)"
FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}&cosd={start}&coed=2025-12-31"
DBN = "https://api.db.nomics.world/v22/series/BLS/cu/{sid}?observations=1&format=json"

AREAS = ["0000", "A101", "A102", "A103", "A207", "A208", "A210", "A211", "A311", "A316", "A318", "A319",
         "A320", "A321", "A421", "A422", "A423", "A424", "A425", "A429", "A433",
         "S11A", "S12A", "S23A", "S23B", "S24A", "S35A", "S35B", "S35C", "S35D", "S37A", "S48A", "S48B",
         "S49A", "S49B", "S49D", "S49E"]
RENT = [f"CU{f}R{a}SEHA" for a in AREAS for f in ("U",)] + [f"CUUS{a}SEHA" for a in AREAS if a != "0000"]
CPI = ["CPIAUCNS", "CUUR0000SA0L2"]
ACS = ("https://api.census.gov/data/{y}/acs/acs1?get=NAME,B25064_001E,B25077_001E,B25103_001E,"
       "B25003_001E,B25003_002E&for=metropolitan%20statistical%20area/micropolitan%20statistical%20area:*")
EXTERNAL = {
    "pmms_MORTGAGE30US.csv": FRED.format(sid="MORTGAGE30US", start="1971-04-02"),
    "damodaran_histretSP_2026.xls": "https://web.archive.org/web/2026id_/https://pages.stern.nyu.edu/~adamodar/pc/datasets/histretSP.xls",
    "damodaran_histretSP_live.xls": "https://pages.stern.nyu.edu/~adamodar/pc/datasets/histretSP.xls",
    "wayback_available.json": "https://archive.org/wayback/available?url=pages.stern.nyu.edu/~adamodar/pc/datasets/histretSP.xls&timestamp=20260201",
}


def get(url: str) -> tuple[int, str, bytes]:
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.status, r.geturl(), r.read()
        except urllib.error.HTTPError as e:
            return e.code, url, e.read() if hasattr(e, "read") else b""
        except (urllib.error.URLError, TimeoutError, OSError):
            time.sleep(5 * (attempt + 1))
    return 0, url, b""


def main() -> int:
    log = open(OUT / "manifest.tsv", "w")
    log.write("kind\tfile\tstatus\tbytes\tsha256\tfinal_url\turl\n")

    def keep(kind: str, path: Path, url: str, store: bool) -> bytes:
        status, final, body = get(url)
        good = status == 200 and body and not body.lstrip().startswith(b"<")
        if store and good:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(body)
        log.write(f"{kind}\t{path.name}\t{status}{'' if good else ' (not kept)'}\t{len(body)}\t"
                  f"{hashlib.sha256(body).hexdigest() if body else '-'}\t{final}\t{url}\n")
        if not good and body:
            (OUT / "errors").mkdir(exist_ok=True)
            (OUT / "errors" / (path.name + ".txt")).write_bytes(body[:4000])
        time.sleep(0.4)
        return body if good else b""

    bls = ROOT / "datasets" / "bls-cpi-rent-us-metros" / "raw"
    for sid in RENT + CPI:
        body = keep("fred-bls", bls / f"{sid}.csv", FRED.format(sid=sid, start="1913-01-01"), True)
        if not body and sid.startswith("CU"):
            keep("dbnomics-bls", bls / f"{sid}.dbnomics.json", DBN.format(sid=sid), True)
    acs = ROOT / "datasets" / "census-acs-housing-costs-msa" / "raw"
    for y in (2010, 2012, 2015, 2019, 2023):
        keep("census-acs", acs / f"acs1_{y}_msa.json", ACS.format(y=y), True)
    for name, url in EXTERNAL.items():
        keep("external", OUT / name, url, False)
    log.close()
    print((OUT / "manifest.tsv").read_text())
    return 0


if __name__ == "__main__":
    sys.exit(main())
