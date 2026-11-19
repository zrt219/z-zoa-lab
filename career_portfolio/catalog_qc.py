"""Descriptive training-catalog QC; never handles the protected holdout."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

REQUIRED = {"object_id", "l_deg", "b_deg", "cz_km_s"}


def describe_catalog(csv_path):
    path = Path(csv_path)
    if any(part.upper() == "HOLDOUT" for part in path.parts):
        raise ValueError("HOLDOUT paths are not accepted by this training utility")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or not REQUIRED.issubset(reader.fieldnames):
            raise ValueError("Expected columns: object_id,l_deg,b_deg,cz_km_s")
        seen, total, masked = set(), 0, 0
        for row in reader:
            obj = row["object_id"].strip()
            lon = float(row["l_deg"])
            lat = float(row["b_deg"])
            radial_velocity = float(row["cz_km_s"])
            if not obj or obj in seen:
                raise ValueError("Missing or duplicate object_id")
            if not (all(map(math.isfinite, (lon, lat, radial_velocity)))
                    and 0 <= lon < 360 and -90 <= lat <= 90):
                raise ValueError("Invalid Galactic coordinates or radial velocity")
            seen.add(obj)
            total += 1
            masked += abs(lat) < 10
    return {
        "status": "training_catalog_descriptive_only",
        "catalog_sha256": digest,
        "objects": total,
        "galactic_zoa_latitude_limit_deg": 10,
        "objects_inside_mask": masked,
        "objects_outside_mask": total - masked,
        "validation": "No holdout, reconstruction or discovery claim; independent verification not performed.",
    }


def main():
    parser = argparse.ArgumentParser(description="Read-only authorized training catalog QA")
    parser.add_argument("--csv", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    report = describe_catalog(args.csv)
    Path(args.out).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
