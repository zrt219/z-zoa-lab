from __future__ import annotations

import os
import sys
import gzip
import csv
import json
import hashlib
import urllib.request
import subprocess
from datetime import datetime, timezone
from pathlib import Path

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def count_file_rows(path: Path) -> int | None:
    """Count non-comment lines or rows in a text/dat/csv file."""
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

def download_stream(url: str, dest_path: Path, headers: dict | None = None, min_bytes: int = 100) -> bool:
    if dest_path.exists() and dest_path.stat().st_size > min_bytes:
        print(f"  [EXISTS] {dest_path.name} ({dest_path.stat().st_size:,} bytes)")
        return True
    
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = dest_path.with_suffix(dest_path.suffix + ".part")
    
    req_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    if headers:
        req_headers.update(headers)
        
    print(f"  [DOWNLOADING] {url} -> {dest_path.name}...")
    try:
        req = urllib.request.Request(url, headers=req_headers)
        with urllib.request.urlopen(req, timeout=120) as resp, temp_path.open("wb") as out_f:
            total = 0
            while True:
                chunk = resp.read(1024 * 1024)
                if not chunk:
                    break
                out_f.write(chunk)
                total += len(chunk)
        if temp_path.stat().st_size < min_bytes:
            temp_path.unlink(missing_ok=True)
            print(f"  [ERROR] File too small ({total} bytes) from {url}")
            return False
        temp_path.replace(dest_path)
        print(f"  [COMPLETED] {dest_path.name} ({dest_path.stat().st_size:,} bytes)")
        return True
    except Exception as e:
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)
        print(f"  [FAILED] {url}: {e}")
        return False

def download_curl(url: str, dest_path: Path) -> bool:
    if dest_path.exists() and dest_path.stat().st_size > 1000:
        print(f"  [EXISTS] {dest_path.name} ({dest_path.stat().st_size:,} bytes)")
        return True
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = dest_path.with_suffix(dest_path.suffix + ".part")
    cmd = [
        "curl.exe", "-k", "-L",
        "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "--output", str(temp_path),
        url
    ]
    print(f"  [CURL] {url} -> {dest_path.name}...")
    res = subprocess.run(cmd, capture_output=True)
    if res.returncode == 0 and temp_path.exists() and temp_path.stat().st_size > 1000:
        temp_path.replace(dest_path)
        print(f"  [COMPLETED] {dest_path.name} ({dest_path.stat().st_size:,} bytes)")
        return True
    else:
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)
        print(f"  [FAILED CURL] {url}")
        return False

def decompress_gz(gz_path: Path, out_path: Path) -> bool:
    if out_path.exists() and out_path.stat().st_size > 0:
        print(f"  [EXISTS UNCOMPRESSED] {out_path.name} ({out_path.stat().st_size:,} bytes)")
        return True
    print(f"  [DECOMPRESSING] {gz_path.name} -> {out_path.name}...")
    try:
        with gzip.open(gz_path, "rb") as f_in, out_path.open("wb") as f_out:
            while chunk := f_in.read(1024 * 1024):
                f_out.write(chunk)
        print(f"  [UNCOMPRESSED] {out_path.name} ({out_path.stat().st_size:,} bytes)")
        return True
    except Exception as e:
        print(f"  [DECOMPRESS ERROR] {gz_path.name}: {e}")
        return False

def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    print(f"=== Z-ZOA Research Dataset Acquisition Engine ===")
    print(f"Repository Root: {repo_root}")

    manifest_entries = []
    failed_downloads = []
    manual_access_catalogues = []

    # -------------------------------------------------------------
    # 1. Cosmicflows-4
    # -------------------------------------------------------------
    print("\n--- [1/6] Downloading Cosmicflows-4 (CF4) Catalogues ---")
    cf4_dir = repo_root / "datasets" / "raw" / "cf4"
    cf4_dir.mkdir(parents=True, exist_ok=True)
    cf4_doi = "10.3847/1538-4357/ac9ab7"
    cf4_citation = "Tully, R. B., et al. 2023, ApJ, 944, 94"

    cf4_items = [
        ("cf4_individual_distances_gz", "table2.dat.gz", "https://cdsarc.cds.unistra.fr/ftp/J/ApJ/944/94/table2.dat.gz", True),
        ("cf4_groups_gz", "groups.dat.gz", "https://cdsarc.cds.unistra.fr/ftp/J/ApJ/944/94/groups.dat.gz", True),
        ("cf4_group_velocities_gz", "table4.dat.gz", "https://cdsarc.cds.unistra.fr/ftp/J/ApJ/944/94/table4.dat.gz", True),
        ("cf4_readme", "ReadMe", "https://cdsarc.cds.unistra.fr/ftp/J/ApJ/944/94/ReadMe", False),
    ]

    for ds_id, fname, url, is_gz in cf4_items:
        dest = cf4_dir / fname
        ok = download_stream(url, dest)
        if ok:
            manifest_entries.append({
                "dataset_id": ds_id,
                "filename": str(dest.relative_to(repo_root)).replace("\\", "/"),
                "source_url": url,
                "doi": cf4_doi,
                "citation": cf4_citation,
                "downloaded_at": utc_now(),
                "sha256": compute_sha256(dest),
                "bytes": dest.stat().st_size,
                "role": "TRAIN",
                "original_file": True,
                "row_count": count_file_rows(dest)
            })
            if is_gz:
                uncomp_name = fname.replace(".gz", "")
                uncomp_dest = cf4_dir / uncomp_name
                if decompress_gz(dest, uncomp_dest):
                    manifest_entries.append({
                        "dataset_id": ds_id.replace("_gz", ""),
                        "filename": str(uncomp_dest.relative_to(repo_root)).replace("\\", "/"),
                        "source_url": url,
                        "doi": cf4_doi,
                        "citation": cf4_citation,
                        "downloaded_at": utc_now(),
                        "sha256": compute_sha256(uncomp_dest),
                        "bytes": uncomp_dest.stat().st_size,
                        "role": "TRAIN",
                        "original_file": False,
                        "row_count": count_file_rows(uncomp_dest)
                    })
        else:
            failed_downloads.append((fname, url))

    # -------------------------------------------------------------
    # 2. Official Cosmicflows Reconstruction Products
    # -------------------------------------------------------------
    print("\n--- [2/6] Downloading Official Cosmicflows Reconstruction Products ---")
    grids_dir = repo_root / "datasets" / "reference" / "cf4_grids"
    cf4pp_dir = repo_root / "datasets" / "reference" / "cf4pp"
    grids_dir.mkdir(parents=True, exist_ok=True)
    cf4pp_dir.mkdir(parents=True, exist_ok=True)

    ip2i_base = "https://projets.ip2i.in2p3.fr/cosmicflows/"
    ip2i_citation = "Graziani, Courtois, et al. / IP2I Cosmicflows Reconstruction"
    ip2i_doi = "10.3847/1538-4357/ac9ab7"

    grid_files = [
        ("cf4_gp_velocity_grid", "CF4gp_new_64-z008_velocity.fits", grids_dir),
        ("cf4_gp_density_grid", "CF4gp_new_64-z008_delta.fits", grids_dir),
        ("cf4_gp_velocity_error_grid", "CF4gp_new_64-z008_velocity_cube_error.fits", grids_dir),
        ("cf4_gp_density_error_grid", "CF4gp_new_64-z008_delta_error.fits", grids_dir),
        ("cf4_velocity_grid", "CF4_new_64-z008_velocity.fits", grids_dir),
        ("cf4_density_grid", "CF4_new_64-z008_delta.fits", grids_dir),
        ("cf4_velocity_error_grid", "CF4_new_64-z008_velocity_cube_error.fits", grids_dir),
        ("cf4_density_error_grid", "CF4_new_64-z008_delta_error.fits", grids_dir),
        ("cf4pp_mean_std_grids", "CF4pp_mean_std_grids.npz", cf4pp_dir),
        ("cf4pp_retrieval_script", "retrieve_CF4pp_grid_values.py", cf4pp_dir),
    ]

    for ds_id, fname, target_dir in grid_files:
        url = ip2i_base + fname
        dest = target_dir / fname
        ok = download_stream(url, dest)
        if ok:
            manifest_entries.append({
                "dataset_id": ds_id,
                "filename": str(dest.relative_to(repo_root)).replace("\\", "/"),
                "source_url": url,
                "doi": ip2i_doi,
                "citation": ip2i_citation,
                "downloaded_at": utc_now(),
                "sha256": compute_sha256(dest),
                "bytes": dest.stat().st_size,
                "role": "COMPARISON_ONLY",
                "original_file": True,
                "row_count": count_file_rows(dest)
            })
        else:
            failed_downloads.append((fname, url))

    # -------------------------------------------------------------
    # 3. 2MRS
    # -------------------------------------------------------------
    print("\n--- [3/6] Downloading 2MASS Redshift Survey (2MRS) ---")
    twomrs_dir = repo_root / "datasets" / "raw" / "2mrs"
    twomrs_dir.mkdir(parents=True, exist_ok=True)
    twomrs_doi = "10.1088/0067-0049/199/2/26"
    twomrs_citation = "Huchra, J. P., et al. 2012, ApJS, 199, 26"

    twomrs_items = [
        ("2mrs_main_catalog_gz", "table3.dat.gz", "https://cdsarc.cds.unistra.fr/ftp/J/ApJS/199/26/table3.dat.gz", True),
        ("2mrs_table6_beyond_limits_gz", "table6.dat.gz", "https://cdsarc.cds.unistra.fr/ftp/J/ApJS/199/26/table6.dat.gz", True),
        ("2mrs_readme", "ReadMe", "https://cdsarc.cds.unistra.fr/ftp/J/ApJS/199/26/ReadMe", False),
    ]

    for ds_id, fname, url, is_gz in twomrs_items:
        dest = twomrs_dir / fname
        ok = download_stream(url, dest)
        if ok:
            manifest_entries.append({
                "dataset_id": ds_id,
                "filename": str(dest.relative_to(repo_root)).replace("\\", "/"),
                "source_url": url,
                "doi": twomrs_doi,
                "citation": twomrs_citation,
                "downloaded_at": utc_now(),
                "sha256": compute_sha256(dest),
                "bytes": dest.stat().st_size,
                "role": "TRAIN",
                "original_file": True,
                "row_count": count_file_rows(dest)
            })
            if is_gz:
                uncomp_name = fname.replace(".gz", "")
                uncomp_dest = twomrs_dir / uncomp_name
                if decompress_gz(dest, uncomp_dest):
                    manifest_entries.append({
                        "dataset_id": ds_id.replace("_gz", ""),
                        "filename": str(uncomp_dest.relative_to(repo_root)).replace("\\", "/"),
                        "source_url": url,
                        "doi": twomrs_doi,
                        "citation": twomrs_citation,
                        "downloaded_at": utc_now(),
                        "sha256": compute_sha256(uncomp_dest),
                        "bytes": uncomp_dest.stat().st_size,
                        "role": "TRAIN",
                        "original_file": False,
                        "row_count": count_file_rows(uncomp_dest)
                    })
        else:
            failed_downloads.append((fname, url))

    # -------------------------------------------------------------
    # 4. HIZOA-S
    # -------------------------------------------------------------
    print("\n--- [4/6] Downloading HIZOA-S (Parkes Southern ZoA) ---")
    hizoa_dir = repo_root / "datasets" / "raw" / "hizoa"
    hizoa_dir.mkdir(parents=True, exist_ok=True)
    hizoa_doi = "10.3847/0004-6256/151/2/52"
    hizoa_citation = "Staveley-Smith, L., et al. 2016, AJ, 151, 52"

    hizoa_items = [
        ("hizoa_table2", "table2.dat", "https://cdsarc.cds.unistra.fr/ftp/J/AJ/151/52/table2.dat"),
        ("hizoa_table3", "table3.dat", "https://cdsarc.cds.unistra.fr/ftp/J/AJ/151/52/table3.dat"),
        ("hizoa_notes", "notes.dat", "https://cdsarc.cds.unistra.fr/ftp/J/AJ/151/52/notes.dat"),
        ("hizoa_readme", "ReadMe", "https://cdsarc.cds.unistra.fr/ftp/J/AJ/151/52/ReadMe"),
    ]

    for ds_id, fname, url in hizoa_items:
        dest = hizoa_dir / fname
        ok = download_stream(url, dest)
        if ok:
            manifest_entries.append({
                "dataset_id": ds_id,
                "filename": str(dest.relative_to(repo_root)).replace("\\", "/"),
                "source_url": url,
                "doi": hizoa_doi,
                "citation": hizoa_citation,
                "downloaded_at": utc_now(),
                "sha256": compute_sha256(dest),
                "bytes": dest.stat().st_size,
                "role": "TRAIN",
                "original_file": True,
                "row_count": count_file_rows(dest)
            })
        else:
            failed_downloads.append((fname, url))

    # -------------------------------------------------------------
    # 5. Vela-SMGPS (HOLDOUT)
    # -------------------------------------------------------------
    print("\n--- [5/6] Acquiring MeerKAT Vela-SMGPS Holdout Materials ---")
    vela_smgps_dir = repo_root / "datasets" / "HOLDOUT" / "vela_smgps"
    vela_smgps_dir.mkdir(parents=True, exist_ok=True)
    vela_smgps_doi = "10.1093/mnras/stae1308"
    vela_smgps_citation = "Kraan-Korteweg, R. C., et al. 2024, MNRAS, 531, 3486"

    # Download paper PDF from arXiv
    paper_pdf = vela_smgps_dir / "Vela-SMGPS_paper.pdf"
    if download_stream("https://arxiv.org/pdf/2405.02983.pdf", paper_pdf, min_bytes=50000):
        manifest_entries.append({
            "dataset_id": "vela_smgps_paper_pdf",
            "filename": str(paper_pdf.relative_to(repo_root)).replace("\\", "/"),
            "source_url": "https://arxiv.org/pdf/2405.02983.pdf",
            "doi": vela_smgps_doi,
            "citation": vela_smgps_citation,
            "downloaded_at": utc_now(),
            "sha256": compute_sha256(paper_pdf),
            "bytes": paper_pdf.stat().st_size,
            "role": "HOLDOUT",
            "original_file": True,
            "row_count": None
        })

    # Download Zenodo Atlas
    atlas_pdf = vela_smgps_dir / "Vela-SMGPS_galaxy_atlas_v2.pdf"
    if download_curl("https://zenodo.org/records/11160742/files/Vela-SMGPS_galaxy_atlas_v2.pdf?download=1", atlas_pdf):
        manifest_entries.append({
            "dataset_id": "vela_smgps_atlas_pdf",
            "filename": str(atlas_pdf.relative_to(repo_root)).replace("\\", "/"),
            "source_url": "https://zenodo.org/records/11160742/files/Vela-SMGPS_galaxy_atlas_v2.pdf?download=1",
            "doi": "10.5281/zenodo.11160742",
            "citation": "Rajohnson et al. 2024, Zenodo Atlas DOI: 10.5281/zenodo.11160742",
            "downloaded_at": utc_now(),
            "sha256": compute_sha256(atlas_pdf),
            "bytes": atlas_pdf.stat().st_size,
            "role": "HOLDOUT",
            "original_file": True,
            "row_count": None
        })

    # Record documentation
    doc_json = vela_smgps_dir / "catalogue_documentation.json"
    doc_data = {
        "survey": "MeerKAT Vela-SMGPS",
        "telescope": "SARAO MeerKAT",
        "paper_title": "HI Galaxy Signatures in the SARAO MeerKAT Galactic Plane Survey – III. Unveiling the obscured part of the Vela Supercluster",
        "authors": "Kraan-Korteweg, R. C., et al.",
        "publication": "MNRAS, 531(3), 3486–3501 (2024)",
        "doi": vela_smgps_doi,
        "zenodo_doi": "10.5281/zenodo.11160742",
        "coverage": "260 <= l <= 290 deg, -2 <= b <= 1 deg, cz up to ~25,000 km/s",
        "detections": 843,
        "known_hizoa_overlaps": 39,
        "holdout_protection": "LOCKED - Training access forbidden"
    }
    doc_json.write_text(json.dumps(doc_data, indent=2), encoding="utf-8")
    manifest_entries.append({
        "dataset_id": "vela_smgps_documentation",
        "filename": str(doc_json.relative_to(repo_root)).replace("\\", "/"),
        "source_url": "https://academic.oup.com/mnras/article/531/3/3486/7682409",
        "doi": vela_smgps_doi,
        "citation": vela_smgps_citation,
        "downloaded_at": utc_now(),
        "sha256": compute_sha256(doc_json),
        "bytes": doc_json.stat().st_size,
        "role": "HOLDOUT",
        "original_file": True,
        "row_count": None
    })

    manual_access_catalogues.append({
        "name": "Vela-SMGPS Full 843-Object ASCII Catalogue (Table A1)",
        "intended_path": "datasets/HOLDOUT/vela_smgps/vela_smgps_full_843.csv",
        "status": "MANUAL-ACCESS-REQUIRED",
        "source": "https://academic.oup.com/mnras/article/531/3/3486/7682409#supplementary-data",
        "reason": "OUP Silverchair/Cloudflare Managed Challenge blocks automated script fetching. Requires manual download via browser session."
    })

    # -------------------------------------------------------------
    # 6. Vela-HI (HOLDOUT)
    # -------------------------------------------------------------
    print("\n--- [6/6] Acquiring MeerKAT Vela-HI Holdout Materials ---")
    vela_hi_dir = repo_root / "datasets" / "HOLDOUT" / "vela_hi"
    vela_hi_dir.mkdir(parents=True, exist_ok=True)
    vela_hi_doi = "10.1093/mnras/stae2499"
    vela_hi_citation = "Courtois, H. M., et al. 2024, MNRAS, 535, 3429"

    # Download Zenodo Atlas
    hi_atlas_pdf = vela_hi_dir / "Vela-HI_galaxy_atlas.pdf"
    if download_curl("https://zenodo.org/records/12522808/files/Vela-HI_galaxy_atlas.pdf?download=1", hi_atlas_pdf):
        manifest_entries.append({
            "dataset_id": "vela_hi_atlas_pdf",
            "filename": str(hi_atlas_pdf.relative_to(repo_root)).replace("\\", "/"),
            "source_url": "https://zenodo.org/records/12522808/files/Vela-HI_galaxy_atlas.pdf?download=1",
            "doi": "10.5281/zenodo.12522808",
            "citation": "Rajohnson et al. 2024, Zenodo Atlas DOI: 10.5281/zenodo.12522808",
            "downloaded_at": utc_now(),
            "sha256": compute_sha256(hi_atlas_pdf),
            "bytes": hi_atlas_pdf.stat().st_size,
            "role": "HOLDOUT",
            "original_file": True,
            "row_count": None
        })

    # Record documentation
    hi_doc_json = vela_hi_dir / "catalogue_documentation.json"
    hi_doc_data = {
        "survey": "MeerKAT Vela-HI",
        "telescope": "SARAO MeerKAT",
        "paper_title": "Revealing Hidden Structures in the Zone of Avoidance – A Blind MeerKAT HI Survey of the Vela Supercluster",
        "authors": "Courtois, H. M., et al.",
        "publication": "MNRAS, 535(4), 3429–3445 (2024)",
        "doi": vela_hi_doi,
        "zenodo_doi": "10.5281/zenodo.12522808",
        "coverage": "263 <= l <= 284 deg, extended Galactic latitude coverage",
        "detections": 719,
        "new_discoveries": 508,
        "holdout_protection": "LOCKED - Training access forbidden"
    }
    hi_doc_json.write_text(json.dumps(hi_doc_data, indent=2), encoding="utf-8")
    manifest_entries.append({
        "dataset_id": "vela_hi_documentation",
        "filename": str(hi_doc_json.relative_to(repo_root)).replace("\\", "/"),
        "source_url": "https://academic.oup.com/mnras/article/535/4/3429/7899964",
        "doi": vela_hi_doi,
        "citation": vela_hi_citation,
        "downloaded_at": utc_now(),
        "sha256": compute_sha256(hi_doc_json),
        "bytes": hi_doc_json.stat().st_size,
        "role": "HOLDOUT",
        "original_file": True,
        "row_count": None
    })

    manual_access_catalogues.append({
        "name": "Vela-HI Full 719-Object Supplementary Catalogue",
        "intended_path": "datasets/HOLDOUT/vela_hi/vela_hi_full_719.csv",
        "status": "MANUAL-ACCESS-REQUIRED",
        "source": "https://academic.oup.com/mnras/article/535/4/3429/7899964#supplementary-data",
        "reason": "OUP Silverchair/Cloudflare Managed Challenge blocks automated script fetching. Requires manual download via browser session."
    })

    # -------------------------------------------------------------
    # Write Manifests
    # -------------------------------------------------------------
    print("\n--- Writing Download Manifests ---")
    manifests_dir = repo_root / "datasets" / "manifests"
    manifests_dir.mkdir(parents=True, exist_ok=True)

    json_manifest_path = manifests_dir / "download_manifest.json"
    csv_manifest_path = manifests_dir / "download_manifest.csv"

    # Write JSON
    manifest_obj = {
        "generated_at": utc_now(),
        "total_files": len(manifest_entries),
        "total_bytes": sum(m["bytes"] for m in manifest_entries),
        "files": manifest_entries,
        "failed_downloads": failed_downloads,
        "manual_access_catalogues": manual_access_catalogues
    }
    json_manifest_path.write_text(json.dumps(manifest_obj, indent=2), encoding="utf-8")
    print(f"Written: {json_manifest_path}")

    # Write CSV
    csv_fields = [
        "dataset_id", "filename", "source_url", "doi", "citation",
        "downloaded_at", "sha256", "bytes", "role", "original_file", "row_count"
    ]
    with csv_manifest_path.open("w", newline="", encoding="utf-8") as f_csv:
        writer = csv.DictWriter(f_csv, fieldnames=csv_fields)
        writer.writeheader()
        for m in manifest_entries:
            writer.writerow(m)
    print(f"Written: {csv_manifest_path}")

    # Print Summary Table
    total_mb = sum(m["bytes"] for m in manifest_entries) / (1024 * 1024)
    print("\n=======================================================")
    print("           Z-ZOA DATASET ACQUISITION SUMMARY           ")
    print("=======================================================")
    print(f"Total files registered: {len(manifest_entries)}")
    print(f"Total disk space consumed: {total_mb:.2f} MB ({sum(m['bytes'] for m in manifest_entries):,} bytes)")
    print(f"Failed downloads: {len(failed_downloads)}")
    print(f"Catalogues requiring manual browser access: {len(manual_access_catalogues)}")
    print("=======================================================\n")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
