# Z-ZOA Paper 1: Master Numerical Reproduction Script
import subprocess
import sys

commands = [
    [sys.executable, "-m", "research.catalogs.inventory"],
    [sys.executable, "-m", "research.catalogs.normalize"],
    [sys.executable, "-m", "research.catalogs.decontamination_pipeline"],
    [sys.executable, "-m", "research.validation.cf4_baseline"],
    [sys.executable, "-m", "research.validation.masks"],
    [sys.executable, "-m", "research.validation.mock_universe"],
    [sys.executable, "-m", "research.reconstruction.engine"],
    [sys.executable, "-m", "research.reconstruction.constrained"],
    [sys.executable, "-m", "research.experiments.freeze"],
    [sys.executable, "-m", "research.validation.leakage_suite"],
    [sys.executable, "-m", "research.holdouts.reveal_gate"],
    [sys.executable, "-m", "research.validation.reveal_and_score"],
    [sys.executable, "-m", "research.reconstruction.hybrid"],
    [sys.executable, "-m", "research.experiments.robustness"],
    [sys.executable, "-m", "research.paper_factory.make_figures"],
    [sys.executable, "-m", "research.paper_factory.make_tables"],
    [sys.executable, "-m", "research.paper_factory.bundle"],
    [sys.executable, "reproducibility/run_acceptance.py"],
]

for cmd in commands:
    print(f"Executing: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
print("All 18 numerical and acceptance stages reproduced cleanly!")

