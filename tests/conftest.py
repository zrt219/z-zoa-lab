"""Pytest test configuration and fixtures."""

from pathlib import Path
import pytest
from research.cosmology.models import CosmologyConfig, COSMOLOGY_PRESETS
from research.catalogs.registry import CatalogRegistry


@pytest.fixture
def planck18_cosmo() -> CosmologyConfig:
    return COSMOLOGY_PRESETS["PLANCK18"]


@pytest.fixture
def cf4_cosmo() -> CosmologyConfig:
    return COSMOLOGY_PRESETS["CF4_NOMINAL"]


@pytest.fixture
def registry() -> CatalogRegistry:
    reg_file = Path("datasets/manifests/catalog_registry.json")
    return CatalogRegistry(registry_file=reg_file)
