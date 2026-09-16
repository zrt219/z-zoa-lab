from __future__ import annotations

import os
import gzip
import json
import csv
import hashlib
from datetime import datetime, timezone
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def count_file_rows(path: Path) -> int | None:
    if not path.is_file():
        return None
    suffix = path.suffix.lower()
    if suffix in [".fits", ".npz", ".pdf", ".gz", ".zip"]:
        return None
    try:
        count = 0
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                s = line.strip()
                if s and not s.startswith("#"):
                    count += 1
        return count
    except Exception:
        return None

def decompress_gz(gz_path: Path, out_path: Path):
    if not out_path.exists() or out_path.stat().st_size == 0:
        print(f"Decompressing {gz_path.name} -> {out_path.name}...")
        with gzip.open(gz_path, "rb") as f_in, out_path.open("wb") as f_out:
            while chunk := f_in.read(1024 * 1024):
                f_out.write(chunk)

# Ensure decompressed files exist
decompress_gz(repo_root / "datasets/raw/cf4/table2.dat.gz", repo_root / "datasets/raw/cf4/table2.dat")
decompress_gz(repo_root / "datasets/raw/cf4/table3.dat.gz", repo_root / "datasets/raw/cf4/table3.dat")
decompress_gz(repo_root / "datasets/raw/cf4/table4.dat.gz", repo_root / "datasets/raw/cf4/table4.dat")
decompress_gz(repo_root / "datasets/raw/2mrs/table3.dat.gz", repo_root / "datasets/raw/2mrs/table3.dat")

# Define all registered research dataset files
entries_spec = [
    # 1. Cosmicflows-4
    {
        "dataset_id": "cf4_individual_distances_original_gz",
        "path": repo_root / "datasets/raw/cf4/table2.dat.gz",
        "source_url": "ftp://cdsarc.cds.unistra.fr/pub/cats/J/ApJ/944/94/table2.dat.gz",
        "doi": "10.3847/1538-4357/ac9ab7",
        "citation": "Tully, R. B., et al. 2023, ApJ, 944, 94",
        "role": "TRAIN",
        "original_file": True
    },
    {
        "dataset_id": "cf4_individual_distances",
        "path": repo_root / "datasets/raw/cf4/table2.dat",
        "source_url": "ftp://cdsarc.cds.unistra.fr/pub/cats/J/ApJ/944/94/table2.dat.gz",
        "doi": "10.3847/1538-4357/ac9ab7",
        "citation": "Tully, R. B., et al. 2023, ApJ, 944, 94",
        "role": "TRAIN",
        "original_file": False
    },
    {
        "dataset_id": "cf4_groups_original_gz",
        "path": repo_root / "datasets/raw/cf4/table3.dat.gz",
        "source_url": "ftp://cdsarc.cds.unistra.fr/pub/cats/J/ApJ/944/94/table3.dat.gz",
        "doi": "10.3847/1538-4357/ac9ab7",
        "citation": "Tully, R. B., et al. 2023, ApJ, 944, 94",
        "role": "TRAIN",
        "original_file": True
    },
    {
        "dataset_id": "cf4_groups",
        "path": repo_root / "datasets/raw/cf4/table3.dat",
        "source_url": "ftp://cdsarc.cds.unistra.fr/pub/cats/J/ApJ/944/94/table3.dat.gz",
        "doi": "10.3847/1538-4357/ac9ab7",
        "citation": "Tully, R. B., et al. 2023, ApJ, 944, 94",
        "role": "TRAIN",
        "original_file": False
    },
    {
        "dataset_id": "cf4_group_velocities_original_gz",
        "path": repo_root / "datasets/raw/cf4/table4.dat.gz",
        "source_url": "ftp://cdsarc.cds.unistra.fr/pub/cats/J/ApJ/944/94/table4.dat.gz",
        "doi": "10.3847/1538-4357/ac9ab7",
        "citation": "Tully, R. B., et al. 2023, ApJ, 944, 94",
        "role": "TRAIN",
        "original_file": True
    },
    {
        "dataset_id": "cf4_group_velocities",
        "path": repo_root / "datasets/raw/cf4/table4.dat",
        "source_url": "ftp://cdsarc.cds.unistra.fr/pub/cats/J/ApJ/944/94/table4.dat.gz",
        "doi": "10.3847/1538-4357/ac9ab7",
        "citation": "Tully, R. B., et al. 2023, ApJ, 944, 94",
        "role": "TRAIN",
        "original_file": False
    },
    {
        "dataset_id": "cf4_readme",
        "path": repo_root / "datasets/raw/cf4/ReadMe",
        "source_url": "ftp://cdsarc.cds.unistra.fr/pub/cats/J/ApJ/944/94/ReadMe",
        "doi": "10.3847/1538-4357/ac9ab7",
        "citation": "Tully, R. B., et al. 2023, ApJ, 944, 94",
        "role": "TRAIN",
        "original_file": True
    },

    # 2. Official Cosmicflows Reconstruction Products
    {
        "dataset_id": "cf4_gp_velocity_grid",
        "path": repo_root / "datasets/reference/cf4_grids/CF4gp_new_64-z008_velocity.fits",
        "source_url": "https://projets.ip2i.in2p3.fr/cosmicflows/CF4gp_new_64-z008_velocity.fits",
        "doi": "10.3847/1538-4357/ac9ab7",
        "citation": "Graziani, Courtois, et al. / IP2I Cosmicflows Reconstruction",
        "role": "COMPARISON_ONLY",
        "original_file": True
    },
    {
        "dataset_id": "cf4_gp_density_grid",
        "path": repo_root / "datasets/reference/cf4_grids/CF4gp_new_64-z008_delta.fits",
        "source_url": "https://projets.ip2i.in2p3.fr/cosmicflows/CF4gp_new_64-z008_delta.fits",
        "doi": "10.3847/1538-4357/ac9ab7",
        "citation": "Graziani, Courtois, et al. / IP2I Cosmicflows Reconstruction",
        "role": "COMPARISON_ONLY",
        "original_file": True
    },
    {
        "dataset_id": "cf4_gp_velocity_error_grid",
        "path": repo_root / "datasets/reference/cf4_grids/CF4gp_new_64-z008_velocity_cube_error.fits",
        "source_url": "https://projets.ip2i.in2p3.fr/cosmicflows/CF4gp_new_64-z008_velocity_cube_error.fits",
        "doi": "10.3847/1538-4357/ac9ab7",
        "citation": "Graziani, Courtois, et al. / IP2I Cosmicflows Reconstruction",
        "role": "COMPARISON_ONLY",
        "original_file": True
    },
    {
        "dataset_id": "cf4_gp_density_error_grid",
        "path": repo_root / "datasets/reference/cf4_grids/CF4gp_new_64-z008_delta_error.fits",
        "source_url": "https://projets.ip2i.in2p3.fr/cosmicflows/CF4gp_new_64-z008_delta_error.fits",
        "doi": "10.3847/1538-4357/ac9ab7",
        "citation": "Graziani, Courtois, et al. / IP2I Cosmicflows Reconstruction",
        "role": "COMPARISON_ONLY",
        "original_file": True
    },
    {
        "dataset_id": "cf4_velocity_grid",
        "path": repo_root / "datasets/reference/cf4_grids/CF4_new_64-z008_velocity.fits",
        "source_url": "https://projets.ip2i.in2p3.fr/cosmicflows/CF4_new_64-z008_velocity.fits",
        "doi": "10.3847/1538-4357/ac9ab7",
        "citation": "Graziani, Courtois, et al. / IP2I Cosmicflows Reconstruction",
        "role": "COMPARISON_ONLY",
        "original_file": True
    },
    {
        "dataset_id": "cf4_density_grid",
        "path": repo_root / "datasets/reference/cf4_grids/CF4_new_64-z008_delta.fits",
        "source_url": "https://projets.ip2i.in2p3.fr/cosmicflows/CF4_new_64-z008_delta.fits",
        "doi": "10.3847/1538-4357/ac9ab7",
        "citation": "Graziani, Courtois, et al. / IP2I Cosmicflows Reconstruction",
        "role": "COMPARISON_ONLY",
        "original_file": True
    },
    {
        "dataset_id": "cf4_velocity_error_grid",
        "path": repo_root / "datasets/reference/cf4_grids/CF4_new_64-z008_velocity_cube_error.fits",
        "source_url": "https://projets.ip2i.in2p3.fr/cosmicflows/CF4_new_64-z008_velocity_cube_error.fits",
        "doi": "10.3847/1538-4357/ac9ab7",
        "citation": "Graziani, Courtois, et al. / IP2I Cosmicflows Reconstruction",
        "role": "COMPARISON_ONLY",
        "original_file": True
    },
    {
        "dataset_id": "cf4_density_error_grid",
        "path": repo_root / "datasets/reference/cf4_grids/CF4_new_64-z008_delta_error.fits",
        "source_url": "https://projets.ip2i.in2p3.fr/cosmicflows/CF4_new_64-z008_delta_error.fits",
        "doi": "10.3847/1538-4357/ac9ab7",
        "citation": "Graziani, Courtois, et al. / IP2I Cosmicflows Reconstruction",
        "role": "COMPARISON_ONLY",
        "original_file": True
    },
    {
        "dataset_id": "cf4pp_mean_std_grids",
        "path": repo_root / "datasets/reference/cf4pp/CF4pp_mean_std_grids.npz",
        "source_url": "https://projets.ip2i.in2p3.fr/cosmicflows/CF4pp_mean_std_grids.npz",
        "doi": "10.3847/1538-4357/ac9ab7",
        "citation": "Graziani, Courtois, et al. / IP2I Cosmicflows CF4++ 10,000 HMC Steps",
        "role": "COMPARISON_ONLY",
        "original_file": True
    },
    {
        "dataset_id": "cf4pp_retrieval_script",
        "path": repo_root / "datasets/reference/cf4pp/retrieve_CF4pp_grid_values.py",
        "source_url": "https://projets.ip2i.in2p3.fr/cosmicflows/retrieve_CF4pp_grid_values.py",
        "doi": "10.3847/1538-4357/ac9ab7",
        "citation": "Graziani, Courtois, et al. / IP2I Cosmicflows",
        "role": "COMPARISON_ONLY",
        "original_file": True
    },

    # 3. 2MRS
    {
        "dataset_id": "2mrs_main_catalog_original_gz",
        "path": repo_root / "datasets/raw/2mrs/table3.dat.gz",
        "source_url": "ftp://cdsarc.cds.unistra.fr/pub/cats/J/ApJS/199/26/table3.dat.gz",
        "doi": "10.1088/0067-0049/199/2/26",
        "citation": "Huchra, J. P., et al. 2012, ApJS, 199, 26",
        "role": "TRAIN",
        "original_file": True
    },
    {
        "dataset_id": "2mrs_main_catalog",
        "path": repo_root / "datasets/raw/2mrs/table3.dat",
        "source_url": "ftp://cdsarc.cds.unistra.fr/pub/cats/J/ApJS/199/26/table3.dat.gz",
        "doi": "10.1088/0067-0049/199/2/26",
        "citation": "Huchra, J. P., et al. 2012, ApJS, 199, 26",
        "role": "TRAIN",
        "original_file": False
    },
    {
        "dataset_id": "2mrs_table6_beyond_limits",
        "path": repo_root / "datasets/raw/2mrs/table6.dat",
        "source_url": "ftp://cdsarc.cds.unistra.fr/pub/cats/J/ApJS/199/26/table6.dat",
        "doi": "10.1088/0067-0049/199/2/26",
        "citation": "Huchra, J. P., et al. 2012, ApJS, 199, 26",
        "role": "TRAIN",
        "original_file": True
    },
    {
        "dataset_id": "2mrs_readme",
        "path": repo_root / "datasets/raw/2mrs/ReadMe",
        "source_url": "ftp://cdsarc.cds.unistra.fr/pub/cats/J/ApJS/199/26/ReadMe",
        "doi": "10.1088/0067-0049/199/2/26",
        "citation": "Huchra, J. P., et al. 2012, ApJS, 199, 26",
        "role": "TRAIN",
        "original_file": True
    },

    # 4. HIZOA-S
    {
        "dataset_id": "hizoa_s_table2",
        "path": repo_root / "datasets/raw/hizoa/table2.dat",
        "source_url": "ftp://cdsarc.cds.unistra.fr/pub/cats/J/AJ/151/52/table2.dat",
        "doi": "10.3847/0004-6256/151/2/52",
        "citation": "Staveley-Smith, L., et al. 2016, AJ, 151, 52",
        "role": "TRAIN",
        "original_file": True
    },
    {
        "dataset_id": "hizoa_s_table3",
        "path": repo_root / "datasets/raw/hizoa/table3.dat",
        "source_url": "ftp://cdsarc.cds.unistra.fr/pub/cats/J/AJ/151/52/table3.dat",
        "doi": "10.3847/0004-6256/151/2/52",
        "citation": "Staveley-Smith, L., et al. 2016, AJ, 151, 52",
        "role": "TRAIN",
        "original_file": True
    },
    {
        "dataset_id": "hizoa_s_notes",
        "path": repo_root / "datasets/raw/hizoa/notes.dat",
        "source_url": "ftp://cdsarc.cds.unistra.fr/pub/cats/J/AJ/151/52/notes.dat",
        "doi": "10.3847/0004-6256/151/2/52",
        "citation": "Staveley-Smith, L., et al. 2016, AJ, 151, 52",
        "role": "TRAIN",
        "original_file": True
    },
    {
        "dataset_id": "hizoa_s_readme",
        "path": repo_root / "datasets/raw/hizoa/ReadMe",
        "source_url": "ftp://cdsarc.cds.unistra.fr/pub/cats/J/AJ/151/52/ReadMe",
        "doi": "10.3847/0004-6256/151/2/52",
        "citation": "Staveley-Smith, L., et al. 2016, AJ, 151, 52",
        "role": "TRAIN",
        "original_file": True
    },

    # 5. Vela-SMGPS (HOLDOUT)
    {
        "dataset_id": "vela_smgps_paper_pdf",
        "path": repo_root / "datasets/HOLDOUT/vela_smgps/Vela-SMGPS_paper.pdf",
        "source_url": "https://arxiv.org/pdf/2405.02983.pdf",
        "doi": "10.1093/mnras/stae1308",
        "citation": "Kraan-Korteweg, R. C., et al. 2024, MNRAS, 531, 3486",
        "role": "HOLDOUT",
        "original_file": True
    },
    {
        "dataset_id": "vela_smgps_atlas_pdf",
        "path": repo_root / "datasets/HOLDOUT/vela_smgps/Vela-SMGPS_galaxy_atlas_v2.pdf",
        "source_url": "https://zenodo.org/records/11160742/files/Vela-SMGPS_galaxy_atlas_v2.pdf?download=1",
        "doi": "10.5281/zenodo.11160742",
        "citation": "Rajohnson et al. 2024, Zenodo Atlas DOI: 10.5281/zenodo.11160742",
        "role": "HOLDOUT",
        "original_file": True
    },
    {
        "dataset_id": "vela_smgps_documentation",
        "path": repo_root / "datasets/HOLDOUT/vela_smgps/catalogue_documentation.json",
        "source_url": "https://academic.oup.com/mnras/article/531/3/3486/7682409",
        "doi": "10.1093/mnras/stae1308",
        "citation": "Kraan-Korteweg, R. C., et al. 2024, MNRAS, 531, 3486",
        "role": "HOLDOUT",
        "original_file": True
    },

    # 6. Vela-HI (HOLDOUT)
    {
        "dataset_id": "vela_hi_atlas_pdf",
        "path": repo_root / "datasets/HOLDOUT/vela_hi/Vela-HI_galaxy_atlas.pdf",
        "source_url": "https://zenodo.org/records/12522808/files/Vela-HI_galaxy_atlas.pdf?download=1",
        "doi": "10.5281/zenodo.12522808",
        "citation": "Rajohnson et al. 2024, Zenodo Atlas DOI: 10.5281/zenodo.12522808",
        "role": "HOLDOUT",
        "original_file": True
    },
    {
        "dataset_id": "vela_hi_documentation",
        "path": repo_root / "datasets/HOLDOUT/vela_hi/catalogue_documentation.json",
        "source_url": "https://academic.oup.com/mnras/article/535/4/3429/7899964",
        "doi": "10.1093/mnras/stae2499",
        "citation": "Courtois, H. M., et al. 2024, MNRAS, 535, 3429",
        "role": "HOLDOUT",
        "original_file": True
    },
]

manifest_entries = []
for spec in entries_spec:
    p: Path = spec["path"]
    if not p.exists():
        print(f"WARNING: Missing expected file: {p}")
        continue
    sz = p.stat().st_size
    h = compute_sha256(p)
    rc = count_file_rows(p)
    entry = {
        "dataset_id": spec["dataset_id"],
        "filename": str(p.relative_to(repo_root)).replace("\\", "/"),
        "source_url": spec["source_url"],
        "doi": spec["doi"],
        "citation": spec["citation"],
        "downloaded_at": utc_now(),
        "sha256": h,
        "bytes": sz,
        "role": spec["role"],
        "original_file": spec["original_file"],
        "row_count": rc
    }
    manifest_entries.append(entry)

manual_access = [
    {
        "dataset_id": "vela_smgps_full_843",
        "name": "MeerKAT Vela-SMGPS Full 843-Object ASCII Catalogue (Table A1)",
        "intended_path": "datasets/HOLDOUT/vela_smgps/vela_smgps_full_843.csv",
        "status": "MANUAL-ACCESS-REQUIRED",
        "source_url": "https://academic.oup.com/mnras/article/531/3/3486/7682409#supplementary-data",
        "doi": "10.1093/mnras/stae1308",
        "citation": "Kraan-Korteweg, R. C., et al. 2024, MNRAS, 531, 3486",
        "role": "HOLDOUT",
        "reason": "OUP Silverchair/Cloudflare Managed Challenge blocks automated script fetching. Requires manual download via browser session."
    },
    {
        "dataset_id": "vela_hi_full_719",
        "name": "MeerKAT Vela-HI Full 719-Object Supplementary Catalogue (Table A1)",
        "intended_path": "datasets/HOLDOUT/vela_hi/vela_hi_full_719.csv",
        "status": "MANUAL-ACCESS-REQUIRED",
        "source_url": "https://academic.oup.com/mnras/article/535/4/3429/7899964#supplementary-data",
        "doi": "10.1093/mnras/stae2499",
        "citation": "Courtois, H. M., et al. 2024, MNRAS, 535, 3429",
        "role": "HOLDOUT",
        "reason": "OUP Silverchair/Cloudflare Managed Challenge blocks automated script fetching. Requires manual download via browser session."
    }
]

# Write manifests
manifests_dir = repo_root / "datasets" / "manifests"
manifests_dir.mkdir(parents=True, exist_ok=True)

manifest_json = manifests_dir / "download_manifest.json"
manifest_csv = manifests_dir / "download_manifest.csv"

out_obj = {
    "generated_at": utc_now(),
    "total_files": len(manifest_entries),
    "total_bytes": sum(m["bytes"] for m in manifest_entries),
    "files": manifest_entries,
    "manual_access_catalogues": manual_access
}
manifest_json.write_text(json.dumps(out_obj, indent=2) + "\n", encoding="utf-8")
print(f"Written: {manifest_json}")

fields = [
    "dataset_id", "filename", "source_url", "doi", "citation",
    "downloaded_at", "sha256", "bytes", "role", "original_file", "row_count"
]
with manifest_csv.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for m in manifest_entries:
        w.writerow(m)
print(f"Written: {manifest_csv}")

print(f"\nFinal Manifest Generation Complete: {len(manifest_entries)} files registered.")
