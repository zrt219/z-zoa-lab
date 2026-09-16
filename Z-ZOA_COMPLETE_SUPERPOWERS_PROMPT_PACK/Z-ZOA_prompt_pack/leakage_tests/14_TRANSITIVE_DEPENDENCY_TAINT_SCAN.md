# Leakage test 14 — Transitive dependency taint scan

Audit ancestral lineage to prevent indirect holdout contamination through parent products.

## Objective

Trace the full Directed Acyclic Graph (DAG) of all training inputs, intermediate tables, merged catalogues, reference grids, and cached features to ensure no ancestor node depended on or ingested protected holdout data (e.g. Vela-SMGPS or Vela-HI).

## Requirements

1. **Cryptographic Lineage Tracking**: Every input product and transformation step must record its upstream parent dataset IDs and SHA-256 digests.
2. **Recursive Graph Traversal**: The audit recursively inspects the dependency tree using depth-first / breadth-first search.
3. **Taint Propagation**: If any ancestor in the lineage graph has the role `HOLDOUT` or is derived from MeerKAT Vela observations, the descendant product is marked `TAINTED_HOLDOUT`.
4. **Automated Enforcement**: Any training execution that attempts to reference a product with a `TAINTED_HOLDOUT` ancestor must be halted immediately.

Save `leakage/14_taint_scan.json` and `.md`.
