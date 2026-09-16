"""FastAPI application gateway for Z-ZOA Calculation Room."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import health, catalogs, calculation, experiments, ledger, reconstruction, validation_routes, reproducibility

app = FastAPI(
    title="Z-ZOA Calculation Room Scientific Gateway",
    description="Minimal REST API exposing cosmology and kinematic kernels for Z-ZOA",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(catalogs.router)
app.include_router(calculation.router)
app.include_router(experiments.router)
app.include_router(ledger.router)
app.include_router(reconstruction.router)
app.include_router(validation_routes.router)
app.include_router(reproducibility.router)



@app.get("/")
def root():
    return {
        "service": "Z-ZOA Calculation Room",
        "description": "CF4-compatible research workspace",
        "docs_url": "/docs",
    }
