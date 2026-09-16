"""Provenance models and lineage record structures."""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ProvenanceRecord(BaseModel):
    """
    Traceable scientific computation record.
    Preserves input, equation, outputs, uncertainties, and data source.
    """
    record_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    action: str = Field(..., description="Action name (e.g. 'peculiar_velocity', 'coordinate_transform')")
    formula: Optional[str] = Field(default=None, description="Mathematical equation or algorithm")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="Input quantities with units")
    outputs: Dict[str, Any] = Field(default_factory=dict, description="Output quantities with units")
    uncertainty: Optional[Dict[str, Any]] = Field(default=None, description="Propagated uncertainty info")
    source: str = Field(..., description="Catalog, instrument, or reference origin")
    reference_frame: Optional[str] = Field(default=None, description="Coordinate or velocity frame")
    notes: Optional[str] = Field(default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
