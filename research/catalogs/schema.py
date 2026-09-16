"""Catalog metadata and data record schemas."""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class DatasetRole(str, Enum):
    TRAIN = "TRAIN"
    TRAIN_CLEAN = "TRAIN_CLEAN"
    HOLDOUT = "HOLDOUT"
    VALIDATION = "VALIDATION"
    COMPARISON_ONLY = "COMPARISON_ONLY"
    REFERENCE = "REFERENCE"
    SYNTHETIC_TEST_ONLY = "SYNTHETIC_TEST_ONLY"
    TRAIN_AFTER_DECONTAMINATION = "TRAIN_AFTER_DECONTAMINATION"


class DatasetMetadata(BaseModel):
    """Metadata schema for all registered datasets in Z-ZOA."""
    dataset_id: str = Field(..., description="Unique slug identifier (e.g. 'cf4_sample')")
    survey: str = Field(..., description="Survey name (e.g. 'Cosmicflows-4', 'MeerKAT Vela-SMGPS')")
    release: str = Field(..., description="Data release designation or table identifier")
    role: DatasetRole = Field(..., description="Scientific role in pipeline")
    file_path: str = Field(..., description="Relative or absolute path to dataset file")
    sha256: str = Field(..., description="Cryptographic SHA-256 checksum of raw data")
    row_count: int = Field(..., ge=0, description="Total galaxy record count")
    columns: List[str] = Field(default_factory=list, description="Column names")
    imported_at: str = Field(..., description="ISO 8601 timestamp of data ingestion")
    citation: str = Field(..., description="Literature DOI or publication citation")
    status: str = Field(default="VERIFIED", description="Verification status (VERIFIED / LOCKED / AUDITED)")
    is_synthetic: bool = Field(default=False, description="Explicit flag for synthetic benchmark data")
    source_url: Optional[str] = Field(default=None, description="Authoritative origin URL")
    doi: Optional[str] = Field(default=None, description="Publication DOI")
    bytes: Optional[int] = Field(default=None, description="Byte size of file")
    parent_dataset_ids: List[str] = Field(default_factory=list, description="Parent lineage dataset IDs")
    transformation_id: Optional[str] = Field(default=None, description="ID of transformation step")
    notes: Optional[str] = Field(default=None, description="Catalog provenance notes")

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
