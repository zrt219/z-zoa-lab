from __future__ import annotations

import os
import sys
import subprocess
from pathlib import Path

def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    os.chdir(repo_root)
    print(f"=== Z-ZOA Dataset Sync & Audit ===")
    print(f"Repo Root: {repo_root}")

    # 1. Run missing dataset acquisition script
    download_script = repo_root / "Z-ZOA_missing_data_bundle" / "download_missing.py"
    if download_script.exists():
        print("\n--- [Step 1/3] Downloading & Updating Catalogues ---")
        res = subprocess.run([sys.executable, str(download_script), "--repo-root", str(repo_root)])
        if res.returncode != 0:
            print("ERROR: Catalog download failed!")
            return res.returncode
    else:
        print("WARNING: Download script not found.")

    # 2. Check manifests
    manifest_file = repo_root / "datasets" / "manifests" / "missing_download_manifest.json"
    print("\n--- [Step 2/3] Manifest Verification ---")
    if manifest_file.exists():
        print(f"Verified Manifest: {manifest_file} ({manifest_file.stat().st_size} bytes)")
    else:
        print("ERROR: Manifest file missing!")
        return 1

    # 3. Run Test Suite
    print("\n--- [Step 3/3] Running Verification Test Suite ---")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root)
    res = subprocess.run([sys.executable, "-m", "pytest"], env=env)
    if res.returncode != 0:
        print("ERROR: Test suite execution failed!")
        return res.returncode

    print("\n=== Sync & Verification Succeeded! ===")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
