"""In-memory and file-backed provenance tracker."""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from research.provenance.models import ProvenanceRecord


class ProvenanceTracker:
    """Manages an append-only linear and DAG provenance trace of calculations."""

    def __init__(self):
        self._records: List[ProvenanceRecord] = []

    def record(self, record: ProvenanceRecord) -> ProvenanceRecord:
        """Append a calculation record to the lineage chain."""
        self._records.append(record)
        return record

    def add(
        self,
        action: str,
        source: str,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        formula: Optional[str] = None,
        uncertainty: Optional[Dict[str, Any]] = None,
        reference_frame: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> ProvenanceRecord:
        """Create and append a new provenance record."""
        rec = ProvenanceRecord(
            action=action,
            source=source,
            inputs=inputs,
            outputs=outputs,
            formula=formula,
            uncertainty=uncertainty,
            reference_frame=reference_frame,
            notes=notes,
        )
        return self.record(rec)

    def get_records(self) -> List[ProvenanceRecord]:
        return list(self._records)

    def to_list(self) -> List[Dict[str, Any]]:
        return [r.to_dict() for r in self._records]

    def clear(self) -> None:
        self._records.clear()
