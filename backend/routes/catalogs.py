"""Catalog registry and data inspection routes."""

from fastapi import APIRouter, HTTPException, Query
from research.catalogs.registry import CatalogRegistry
from research.catalogs.loader import load_dataset_table
from research.holdouts.guard import DataGateway, ExecutionContext, ExecutionMode
from research.holdouts.exceptions import HoldoutLeakageViolationError, UnfrozenValidationViolationError
from backend.config import REGISTRY_PATH, BASE_DIR

router = APIRouter(prefix="/catalogs", tags=["catalogs"])


def get_registry() -> CatalogRegistry:
    return CatalogRegistry(registry_file=REGISTRY_PATH)


@router.get("/")
def list_catalogs():
    reg = get_registry()
    datasets = reg.list_all()
    return [d.to_dict() for d in datasets]


@router.get("/{dataset_id}/inspect")
def inspect_catalog(
    dataset_id: str,
    mode: str = Query("TRAINING", description="TRAINING or VALIDATION"),
    freeze_token: str = Query(None, description="Freeze token for HOLDOUT access"),
):
    reg = get_registry()
    try:
        meta = reg.get(dataset_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset_id}' not found.")

    gateway = DataGateway(reg, base_dir=BASE_DIR)
    ctx = ExecutionContext(
        run_id="API_INSPECT",
        mode=ExecutionMode(mode.upper()),
        freeze_token=freeze_token,
    )

    try:
        df = gateway.request_dataset(dataset_id, ctx)
        preview_rows = df.head(50).to_dicts()
        return {
            "metadata": meta.to_dict(),
            "total_rows": df.height,
            "preview_rows": preview_rows,
        }
    except (HoldoutLeakageViolationError, UnfrozenValidationViolationError) as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
