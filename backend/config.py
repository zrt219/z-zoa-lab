"""Backend configuration settings."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
REGISTRY_PATH = BASE_DIR / "datasets" / "manifests" / "catalog_registry.json"
RUNS_DIR = BASE_DIR / "runs"
