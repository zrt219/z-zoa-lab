"""Central catalog registry for managing astronomical survey data."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Union

from research.catalogs.schema import DatasetMetadata, DatasetRole


class CatalogRegistry:
    """In-memory and file-backed dataset catalog registry."""

    def __init__(self, registry_file: Optional[Union[str, Path]] = None):
        self._registry: Dict[str, DatasetMetadata] = {}
        self.registry_file = Path(registry_file) if registry_file else None
        if self.registry_file and self.registry_file.exists():
            self.load_from_disk(self.registry_file)

    def register(self, metadata: DatasetMetadata) -> None:
        """Register or update a dataset."""
        self._registry[metadata.dataset_id] = metadata
        if self.registry_file:
            self.save_to_disk(self.registry_file)

    def get(self, dataset_id: str) -> DatasetMetadata:
        """Retrieve dataset metadata by ID."""
        if dataset_id not in self._registry:
            raise KeyError(f"Dataset '{dataset_id}' not found in registry.")
        return self._registry[dataset_id]

    def list_all(self) -> List[DatasetMetadata]:
        """List all registered datasets."""
        return list(self._registry.values())

    def filter_by_role(self, role: DatasetRole) -> List[DatasetMetadata]:
        """Filter registered datasets by role."""
        return [d for d in self._registry.values() if d.role == role]

    def save_to_disk(self, path: Path) -> None:
        """Persist registry to JSON file."""
        data = {d_id: meta.to_dict() for d_id, meta in self._registry.items()}
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_from_disk(self, path: Path) -> None:
        """Load registry from JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for d_id, item in data.items():
                self._registry[d_id] = DatasetMetadata(**item)
