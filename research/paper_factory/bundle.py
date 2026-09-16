"""Reproducibility bundle generator for Z-ZOA Paper 1 (Prompt 17).

Creates a self-contained ZIP archive containing all code, configs, manifests,
reproducibility scripts, publication tables, and figures needed to verify
the central scientific claims of the paper.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List
import zipfile


def sha256_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with filepath.open("rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def create_reproducibility_bundle(
    repo_root: Path,
    output_zip: Path | None = None,
) -> Dict[str, Any]:
    if output_zip is None:
        output_zip = repo_root / "reproducibility" / "Z_ZOA_REPRODUCIBILITY_BUNDLE.zip"

    output_zip.parent.mkdir(parents=True, exist_ok=True)

    included_patterns = [
        "research/**/*.py",
        "configs/**/*.yaml",
        "datasets/manifests/*.json",
        "datasets/manifests/*.csv",
        "leakage/*.json",
        "leakage/*.parquet",
        "leakage/*.md",
        "runs/VELA-001/*.json",
        "runs/VELA-001/*.sha256",
        "paper/tables/*",
        "paper/figures/*",
        "docs/*.md",
        "docs/*.csv",
        "docs/*.json",
        "reproducibility/*.py",
        "reproducibility/*.md",
        "reproducibility/*.txt",
        "pyproject.toml",
    ]

    files_to_pack: List[Path] = []
    for pattern in included_patterns:
        for p in repo_root.glob(pattern):
            if p.is_file() and not p.name.endswith(".zip"):
                files_to_pack.append(p)

    files_to_pack = sorted(list(set(files_to_pack)))
    file_manifest: List[Dict[str, Any]] = []

    with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in files_to_pack:
            rel_path = p.relative_to(repo_root).as_posix()
            zf.write(p, arcname=rel_path)
            file_manifest.append({
                "path": rel_path,
                "bytes": p.stat().st_size,
                "sha256": sha256_file(p),
            })

    manifest_data = {
        "bundle_name": output_zip.name,
        "bundle_sha256": sha256_file(output_zip),
        "total_files": len(file_manifest),
        "total_bytes": output_zip.stat().st_size,
        "run_id": "VELA-001",
        "files": file_manifest,
    }

    manifest_path = repo_root / "reproducibility" / "BUNDLE_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")

    return {
        "bundle_path": str(output_zip),
        "bundle_bytes": output_zip.stat().st_size,
        "bundle_sha256": manifest_data["bundle_sha256"],
        "files_packed": len(file_manifest),
        "manifest_path": str(manifest_path),
    }


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parent.parent.parent
    res = create_reproducibility_bundle(repo_root)
    print("Bundle created:")
    print(json.dumps(res, indent=2))
