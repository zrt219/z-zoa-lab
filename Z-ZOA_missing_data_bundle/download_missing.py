from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

from astroquery.vizier import Vizier
from pyvo.dal import TAPService


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def download_ga_smgps(repo: Path) -> dict:
    outdir = repo / "datasets" / "HOLDOUT" / "GA_SMGPS"
    outdir.mkdir(parents=True, exist_ok=True)
    csv_path = outdir / "ga_smgps_477.csv"

    viz = Vizier(columns=["**"])
    viz.ROW_LIMIT = -1
    tables = viz.get_catalogs("J/MNRAS/529/L88/ga-smgps")
    if not tables:
        raise RuntimeError("VizieR returned no GA-SMGPS table")
    table = tables[0]
    if len(table) != 477:
        raise RuntimeError(f"GA-SMGPS row-count check failed: expected 477, got {len(table)}")
    table.write(csv_path, format="ascii.csv", overwrite=True)

    record = {
        "dataset_id": "GA_SMGPS_2024",
        "role": "HOLDOUT",
        "training_access": False,
        "catalogue": "J/MNRAS/529/L88/ga-smgps",
        "rows": len(table),
        "source_url": "https://vizier.cds.unistra.fr/viz-bin/VizieR?-source=J/MNRAS/529/L88",
        "doi": "10.1093/mnrasl/slad196",
        "citation": "Steyn et al. 2024, MNRAS Letters, 529, L88-L94",
        "downloaded_at": utc_now(),
        "filename": str(csv_path.relative_to(repo)),
        "sha256": sha256(csv_path),
        "bytes": csv_path.stat().st_size,
        "original_service": "VizieR",
        "note": "Exported losslessly from the public VizieR table to CSV; treat as holdout/future-validation data."
    }
    write_json(outdir / "ga_smgps_source.json", record)
    return record


def download_wallaby_dr2(repo: Path) -> dict:
    outdir = repo / "datasets" / "reference" / "WALLABY_DR2"
    outdir.mkdir(parents=True, exist_ok=True)
    csv_path = outdir / "wallaby_dr2_source_catalogue.csv"

    service = TAPService("https://ws-uv.canfar.net/youcat")
    count_result = service.run_sync(
        "SELECT COUNT(*) AS n FROM cirada.Wallaby_dr2_source_catalogue",
        maxrec=10,
    ).to_table()
    expected_remote_rows = int(count_result[0][0])

    result = service.run_sync(
        "SELECT * FROM cirada.Wallaby_dr2_source_catalogue",
        maxrec=max(expected_remote_rows + 100, 10000),
    )
    table = result.to_table()
    if len(table) != expected_remote_rows:
        raise RuntimeError(
            f"WALLABY DR2 row-count check failed: TAP COUNT={expected_remote_rows}, downloaded={len(table)}"
        )
    if len(table) < 1760:
        raise RuntimeError(f"WALLABY DR2 unexpectedly small: {len(table)} rows")
    table.write(csv_path, format="ascii.csv", overwrite=True)

    record = {
        "dataset_id": "WALLABY_PILOT_DR2_30ARCSEC",
        "role": "COMPARISON_ONLY",
        "catalogue": "cirada.Wallaby_dr2_source_catalogue",
        "rows": len(table),
        "source_url": "https://ws-uv.canfar.net/youcat",
        "release_url": "https://wallaby-survey.org/data/data-pilot-survey-dr2/",
        "doi": "10.25919/qw7w-tn96",
        "citation": "Murugeshan et al. 2024, PASA, 41, e088 (arXiv:2409.13130)",
        "downloaded_at": utc_now(),
        "filename": str(csv_path.relative_to(repo)),
        "sha256": sha256(csv_path),
        "bytes": csv_path.stat().st_size,
        "original_service": "CADC/CANFAR YouCat TAP",
        "note": "Keep comparison-only until leakage/validation boundaries are explicitly defined."
    }
    write_json(outdir / "wallaby_dr2_source.json", record)
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description="Download missing Z-ZOA public catalogues")
    parser.add_argument("--repo-root", default=".", help="Z-ZOA repository root")
    args = parser.parse_args()
    repo = Path(args.repo_root).resolve()
    (repo / "datasets" / "manifests").mkdir(parents=True, exist_ok=True)

    print(f"Repo root: {repo}")
    print("Downloading GA-SMGPS from VizieR...")
    ga = download_ga_smgps(repo)
    print(f"  OK: {ga['rows']} rows, sha256={ga['sha256']}")

    print("Downloading WALLABY Pilot DR2 from CADC/CANFAR TAP...")
    wallaby = download_wallaby_dr2(repo)
    print(f"  OK: {wallaby['rows']} rows, sha256={wallaby['sha256']}")

    manifest = {
        "created_at": utc_now(),
        "tool": "Z-ZOA missing-data acquisition bundle",
        "python": sys.version,
        "platform": platform.platform(),
        "datasets": [ga, wallaby],
    }
    manifest_path = repo / "datasets" / "manifests" / "missing_download_manifest.json"
    write_json(manifest_path, manifest)
    print(f"Manifest: {manifest_path}")
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
