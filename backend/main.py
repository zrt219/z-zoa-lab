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



import os
from fastapi.staticfiles import StaticFiles

# Mount runs and paper directories for direct file inspection and downloads
runs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "runs"))
if os.path.exists(runs_dir):
    app.mount("/runs", StaticFiles(directory=runs_dir, html=True), name="runs")

paper_figures_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "paper", "figures"))
if os.path.exists(paper_figures_dir):
    app.mount("/paper/figures", StaticFiles(directory=paper_figures_dir, html=True), name="paper_figures")

paper_tables_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "paper", "tables"))
if os.path.exists(paper_tables_dir):
    app.mount("/paper/tables", StaticFiles(directory=paper_tables_dir, html=True), name="paper_tables")

from fastapi.responses import HTMLResponse, FileResponse

# Direct Web-Viewable Study Article & ELI5 Overview
@app.get("/study", response_class=HTMLResponse)
def get_study_page():
    template_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "templates", "study.html"))
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Study Page Not Found</h1>", status_code=404)

# Mount frontend build if available, while keeping all API routes intact
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
else:
    @app.get("/")
    def root():
        return {
            "service": "Z-ZOA Calculation Room",
            "description": "CF4-compatible research workspace",
            "docs_url": "/docs",
        }

