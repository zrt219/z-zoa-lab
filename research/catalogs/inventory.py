"""Dataset inventory and audit generator for Z-ZOA."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List
import polars as pl


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def count_rows(path: Path) -> int:
    if path.suffix == ".parquet":
        return pl.read_parquet(path).height
    elif path.suffix == ".csv":
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            count = 0
            for row in reader:
                if not row or (len(row) == 1 and row[0].startswith("#")):
                    continue
                count += 1
            return max(0, count - 1)  # subtract header
    return 0


def generate_inventory(base_dir: Path) -> Dict[str, Any]:
    manifests_dir = base_dir / "datasets" / "manifests"
    manifests_dir.mkdir(parents=True, exist_ok=True)

    # Core defined dataset catalog inventory targets
    inventory_items = [
        {
            "dataset_id": "cf4_sample",
            "name": "Cosmicflows-4 Sample Distances",
            "survey": "Cosmicflows-4",
            "release": "Tully et al. 2023, ApJ 944, 94",
            "role": "TRAIN",
            "relative_path": "datasets/raw/cf4/cf4_sample.parquet",
            "source_url": "https://edd.ifa.hawaii.edu/",
            "doi": "10.3847/1538-4357/ac9ab7",
            "citation": "Tully, R. B., et al. 2023, ApJ, 944, 94",
            "expected_role": "TRAIN",
        },
        {
            "dataset_id": "hizoa_s_sample",
            "name": "HIZOA-S Benchmark Sample",
            "survey": "HIZOA-S (Parkes Southern ZoA)",
            "release": "Staveley-Smith et al. 2016, AJ 151, 52 (Table 2)",
            "role": "TRAIN_AFTER_DECONTAMINATION",
            "relative_path": "datasets/raw/hizoa/hizoa_sample.parquet",
            "source_url": "https://vizier.cds.unistra.fr/viz-bin/VizieR?-source=J/AJ/151/52",
            "doi": "10.3847/0004-6256/151/2/52",
            "citation": "Staveley-Smith, L., et al. 2016, AJ, 151, 52",
            "expected_role": "TRAIN_AFTER_DECONTAMINATION",
        },
        {
            "dataset_id": "hizoa_s_full",
            "name": "HIZOA-S Full Catalog",
            "survey": "HIZOA-S (Parkes Southern ZoA)",
            "release": "Staveley-Smith et al. 2016, AJ 151, 52",
            "role": "TRAIN_AFTER_DECONTAMINATION",
            "relative_path": "datasets/raw/hizoa/hizoa_s_full.csv",
            "source_url": "https://vizier.cds.unistra.fr/viz-bin/VizieR?-source=J/AJ/151/52",
            "doi": "10.3847/0004-6256/151/2/52",
            "citation": "Staveley-Smith, L., et al. 2016, AJ, 151, 52",
            "expected_role": "TRAIN_AFTER_DECONTAMINATION",
        },
        {
            "dataset_id": "2mrs_sample",
            "name": "2MASS Redshift Survey Sample",
            "survey": "2MRS",
            "release": "Huchra et al. 2012 / Macri et al. 2019",
            "role": "TRAIN",
            "relative_path": "datasets/raw/2mrs/2mrs_sample.csv",
            "source_url": "https://vizier.cds.unistra.fr/viz-bin/VizieR?-source=J/ApJS/199/26",
            "doi": "10.1088/0067-0049/199/2/26",
            "citation": "Huchra, J. P., et al. 2012, ApJS, 199, 26",
            "expected_role": "TRAIN",
        },
        {
            "dataset_id": "vela_smgps_sample",
            "name": "MeerKAT Vela-SMGPS Benchmark Sample",
            "survey": "MeerKAT Vela-SMGPS",
            "release": "Kraan-Korteweg et al. 2024, MNRAS 531, 3486",
            "role": "HOLDOUT",
            "relative_path": "datasets/HOLDOUT/vela_smgps/vela_smgps_sample.parquet",
            "source_url": "https://academic.oup.com/mnras/article/531/3/3486/7682409",
            "doi": "10.1093/mnras/stae1308",
            "citation": "Kraan-Korteweg, R. C., et al. 2024, MNRAS, 531, 3486",
            "expected_role": "HOLDOUT",
        },
        {
            "dataset_id": "ga_smgps_477",
            "name": "MeerKAT GA-SMGPS Great Attractor Catalogue",
            "survey": "MeerKAT GA-SMGPS",
            "release": "Steyn et al. 2024, MNRAS Letters, 529, L88-L94",
            "role": "HOLDOUT",
            "relative_path": "datasets/HOLDOUT/ga_smgps/ga_smgps_477.csv",
            "source_url": "https://vizier.cds.unistra.fr/viz-bin/VizieR?-source=J/MNRAS/529/L88",
            "doi": "10.1093/mnrasl/slad196",
            "citation": "Steyn, et al. 2024, MNRAS Letters, 529, L88-L94",
            "expected_role": "HOLDOUT",
        },
        {
            "dataset_id": "wallaby_dr2",
            "name": "WALLABY Pilot Survey DR2",
            "survey": "ASKAP WALLABY",
            "release": "Murugeshan et al. 2024, PASA, 41, e088",
            "role": "COMPARISON_ONLY",
            "relative_path": "datasets/reference/wallaby_dr2/wallaby_dr2_source_catalogue.csv",
            "source_url": "https://ws-uv.canfar.net/youcat",
            "doi": "10.25919/qw7w-tn96",
            "citation": "Murugeshan et al. 2024, PASA, 41, e088",
            "expected_role": "COMPARISON_ONLY",
        },
        {
            "dataset_id": "vela_smgps_full_843",
            "name": "MeerKAT Vela-SMGPS Full 843 Catalog",
            "survey": "MeerKAT Vela-SMGPS",
            "release": "Kraan-Korteweg et al. 2024 (Table A1/Online)",
            "role": "HOLDOUT",
            "relative_path": "datasets/HOLDOUT/vela_smgps/vela_smgps_full_843.csv",
            "source_url": "https://academic.oup.com/mnras/article/531/3/3486/7682409",
            "doi": "10.1093/mnras/stae1308",
            "citation": "Kraan-Korteweg, R. C., et al. 2024, MNRAS, 531, 3486",
            "expected_role": "HOLDOUT",
        },
        {
            "dataset_id": "vela_hi_full_719",
            "name": "MeerKAT Vela-HI Full 719 Catalog",
            "survey": "MeerKAT Vela-HI",
            "release": "Courtois et al. (in prep / team release)",
            "role": "HOLDOUT",
            "relative_path": "datasets/HOLDOUT/vela_hi/vela_hi_full_719.csv",
            "source_url": "https://academic.oup.com/mnras/article/531/3/3486/7682409",
            "doi": "10.1093/mnras/stae1308",
            "citation": "Vela-HI Collaboration (2024)",
            "expected_role": "HOLDOUT",
        },
        {
            "dataset_id": "cf4_density_grid_official",
            "name": "Cosmicflows-4 Official Density Grid",
            "survey": "Cosmicflows-4",
            "release": "Graziani et al. / Tully et al. 2023",
            "role": "REFERENCE",
            "relative_path": "datasets/reference/cf4_grids/CF4_new_64-z008_delta.fits",
            "source_url": "https://edd.ifa.hawaii.edu/",
            "doi": "10.3847/1538-4357/ac9ab7",
            "citation": "Tully et al. 2023 / Graziani et al.",
            "expected_role": "REFERENCE",
        },
        {
            "dataset_id": "cf4_velocity_grid_official",
            "name": "Cosmicflows-4 Official Velocity Grid",
            "survey": "Cosmicflows-4",
            "release": "Graziani et al. / Tully et al. 2023",
            "role": "REFERENCE",
            "relative_path": "datasets/reference/cf4_grids/CF4_new_64-z008_velocity.fits",
            "source_url": "https://edd.ifa.hawaii.edu/",
            "doi": "10.3847/1538-4357/ac9ab7",
            "citation": "Tully et al. 2023 / Graziani et al.",
            "expected_role": "REFERENCE",
        },
        {
            "dataset_id": "cf4pp_mean_std_grids",
            "name": "CF4++ Density and Velocity Mean/Std Grids",
            "survey": "Cosmicflows-4++",
            "release": "Courtois et al. / Tully et al.",
            "role": "REFERENCE",
            "relative_path": "datasets/reference/cf4pp/CF4pp_mean_std_grids.npz",
            "source_url": "https://edd.ifa.hawaii.edu/",
            "doi": "10.3847/1538-4357/ac9ab7",
            "citation": "Courtois et al. (CF4++)",
            "expected_role": "REFERENCE",
        },
    ]

    records = []
    missing_records = []
    checksum_lines = []

    for item in inventory_items:
        file_p = base_dir / item["relative_path"]
        exists = file_p.exists()
        if exists:
            sha = compute_sha256(file_p)
            size = file_p.stat().st_size
            rows = count_rows(file_p)
            status = "PRESENT"
            rec = {
                **item,
                "status": status,
                "sha256": sha,
                "bytes": size,
                "row_count": rows,
                "file_path": str(file_p.relative_to(base_dir)).replace("\\", "/"),
            }
            records.append(rec)
            checksum_lines.append(f"{sha}  {rec['file_path']}")
        else:
            status = "MANUAL-ACCESS-REQUIRED"
            rec = {
                **item,
                "status": status,
                "sha256": None,
                "bytes": None,
                "row_count": None,
                "file_path": item["relative_path"],
                "reason": "Official full data release requires direct download or journal supplementary extraction.",
            }
            missing_records.append(rec)
            records.append(rec)

    # Write inventory.json
    inv_json = manifests_dir / "inventory.json"
    with inv_json.open("w", encoding="utf-8") as f:
        json.dump({"inventory": records}, f, indent=2)

    # Write inventory.csv
    inv_csv = manifests_dir / "inventory.csv"
    fieldnames = [
        "dataset_id", "name", "survey", "release", "role",
        "file_path", "status", "row_count", "bytes", "sha256", "doi", "source_url"
    ]
    with inv_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            filtered = {k: r.get(k) for k in fieldnames}
            writer.writerow(filtered)

    # Write missing.json
    miss_json = manifests_dir / "missing.json"
    with miss_json.open("w", encoding="utf-8") as f:
        json.dump({"missing": missing_records}, f, indent=2)

    # Write checksums.sha256
    chk_file = manifests_dir / "checksums.sha256"
    with chk_file.open("w", encoding="utf-8") as f:
        f.write("\n".join(checksum_lines) + "\n")

    return {
        "total_inventoried": len(records),
        "present": len([r for r in records if r["status"] == "PRESENT"]),
        "missing": len(missing_records),
        "records": records,
    }


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parent.parent.parent
    res = generate_inventory(repo_root)
    print(f"Inventory generated: {res['present']} PRESENT, {res['missing']} MANUAL-ACCESS-REQUIRED.")
