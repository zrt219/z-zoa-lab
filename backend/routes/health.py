"""Health and system status route."""

from fastapi import APIRouter
from research.experiments.manifest import get_environment_versions, get_git_commit

router = APIRouter()


@router.get("/health")
def get_health():
    return {
        "status": "healthy",
        "service": "Z-ZOA Calculation Room Scientific Gateway",
        "git_commit": get_git_commit(),
        "versions": get_environment_versions(),
    }
