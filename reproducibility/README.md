# Z-ZOA Paper 1 Reproducibility Bundle

**Experiment Run ID**: `VELA-001`  
**Packaged At**: 2026-09-15T11:05:31.050572+00:00  

This bundle contains all frozen configurations, cryptographic manifests, exclusion lists,
validation metrics, null-hypothesis distributions, and figure-generation assets required to
independently reproduce all numerical claims in:

**Z-ZOA: Out-of-Sample Reconstruction and H I Validation of Large-Scale Structure Across the Galactic Zone of Avoidance**

## Exact Run Order
To reproduce from scratch, execute in sequence:
1. `python -m research.catalogs.inventory`
2. `python -m research.catalogs.normalize`
3. `python -m research.catalogs.decontamination_pipeline`
4. `python -m research.validation.cf4_baseline`
5. `python -m research.validation.masks`
6. `python -m research.validation.mock_universe`
7. `python -m research.reconstruction.engine`
8. `python -m research.reconstruction.constrained`
9. `python -m research.experiments.freeze`
10. `python -m research.validation.leakage_suite`
11. `python -m research.validation.reveal_and_score`
12. `python -m research.reconstruction.hybrid`
13. `python -m research.experiments.robustness`
14. `python -m research.experiments.paper_factory`

Or simply run:
```bash
python reproducibility/REPRODUCE_ALL.py
```
