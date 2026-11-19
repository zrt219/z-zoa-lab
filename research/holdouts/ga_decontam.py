"""GA-001 footprint decontamination (Great Attractor / Norma ZoA).

Builds a GA-specific TRAIN_CLEAN snapshot by quarantining every training tracer
(HIZOA-S, CF4, 2MRS) that falls inside the *published* GA-SMGPS footprint plus a
safety buffer.

Holdout-blindness invariant
---------------------------
This module NEVER reads the GA-SMGPS holdout (raw CSV or any normalized copy).
The quarantine volume is defined purely from survey geometry
(``research.masks.selection_functions.SURVEY_FOOTPRINTS["GA_SMGPS"]``, which is a
conservative superset of Steyn et al. 2024, MNRAS Letters 529, L88:
302 deg <= l <= 332 deg inside the SMGPS |b| <~ 1.5 deg strip).

The Vela TRAIN_CLEAN snapshot (N = 902) is left untouched.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import polars as pl

from research.masks.selection_functions import get_survey_footprint

RUN_ID = "GA-001"
BUFFER_DEG = 1.0  # extra angular margin around the published footprint
CZ_BUFFER_KMS = 1000.0

TRAIN_SOURCES = {
    "hizoa_s_full": "hizoa_s_full_normalized.parquet",
    "cf4_sample": "cf4_sample_normalized.parquet",
    "2mrs_sample": "2mrs_sample_normalized.parquet",
}

# Files that must never be opened by this module.
FORBIDDEN_TOKENS = ("ga_smgps", "vela_smgps", "holdout")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def quarantine_volume() -> Dict[str, float]:
    """Return the buffered GA quarantine volume (geometry only)."""
    fp = get_survey_footprint("GA_SMGPS")
    return {
        "l_min_deg": fp.l_min_deg - BUFFER_DEG,
        "l_max_deg": fp.l_max_deg + BUFFER_DEG,
        "b_min_deg": fp.b_min_deg - BUFFER_DEG,
        "b_max_deg": fp.b_max_deg + BUFFER_DEG,
        "cz_max_kms": fp.cz_max_kms + CZ_BUFFER_KMS,
        "footprint_source": fp.notes,
        "buffer_deg": BUFFER_DEG,
        "cz_buffer_kms": CZ_BUFFER_KMS,
    }


def in_quarantine(df: pl.DataFrame, vol: Dict[str, float]) -> pl.Expr:
    # Sky-only cut (velocity-agnostic) is the conservative choice: any tracer on
    # the GA sky patch is quarantined regardless of its cz.
    return (
        (pl.col("gal_l_deg") >= vol["l_min_deg"])
        & (pl.col("gal_l_deg") <= vol["l_max_deg"])
        & (pl.col("gal_b_deg") >= vol["b_min_deg"])
        & (pl.col("gal_b_deg") <= vol["b_max_deg"])
    )


def run_ga_decontamination(repo_root: Path) -> Dict[str, Any]:
    norm_dir = repo_root / "datasets" / "processed" / "normalized"
    out_dir = repo_root / "datasets" / "processed" / "TRAIN_CLEAN_GA"
    leak_dir = repo_root / "leakage" / "ga"
    out_dir.mkdir(parents=True, exist_ok=True)
    leak_dir.mkdir(parents=True, exist_ok=True)

    vol = quarantine_volume()
    excluded: List[pl.DataFrame] = []
    clean: List[pl.DataFrame] = []
    per_source: Dict[str, Any] = {}
    inputs: Dict[str, str] = {}

    for dataset_id, fname in TRAIN_SOURCES.items():
        assert not any(t in fname.lower() for t in FORBIDDEN_TOKENS), fname
        path = norm_dir / fname
        if not path.exists():
            raise FileNotFoundError(f"Missing normalized TRAIN input: {path}")
        inputs[dataset_id] = _sha256(path)
        df = pl.read_parquet(path)
        mask = in_quarantine(df, vol)
        ex = df.filter(mask).with_columns(
            pl.lit(dataset_id).alias("source_dataset"),
            pl.lit("Tracer inside buffered GA-SMGPS footprint (geometry-only quarantine)").alias("reason"),
        )
        cl = df.filter(~mask)
        excluded.append(ex)
        clean.append(cl)
        cl.write_parquet(out_dir / fname.replace("_normalized", "_clean_ga"))
        per_source[dataset_id] = {"input_rows": df.height, "excluded_rows": ex.height, "clean_rows": cl.height}

    excl_df = pl.concat(excluded, how="diagonal_relaxed") if excluded else pl.DataFrame()
    clean_df = pl.concat(clean, how="diagonal_relaxed")
    excl_path = leak_dir / "exclusion_list_ga.parquet"
    clean_path = out_dir / "train_clean_ga_combined.parquet"
    excl_df.write_parquet(excl_path)
    clean_df.write_parquet(clean_path)

    summary = {
        "pipeline_version": "Z-ZOA-GA-DECONTAM-v1.0",
        "run_id": RUN_ID,
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "holdout_files_read": [],
        "quarantine_volume": vol,
        "input_sha256": inputs,
        "per_source": per_source,
        "total_excluded": excl_df.height,
        "total_train_clean_ga": clean_df.height,
        "exclusion_list_sha256": _sha256(excl_path),
        "train_clean_ga_sha256": _sha256(clean_path),
        "clean_output_path": str(clean_path.relative_to(repo_root)).replace("\\", "/"),
    }
    (leak_dir / "ga_decontam_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent.parent
    print(json.dumps(run_ga_decontamination(root), indent=2))
