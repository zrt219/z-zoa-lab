---
name: {SKILL_NAME}
description: >-
  {SKILL_DESCRIPTION}
---

# {SKILL_TITLE}

## Overview

{BRIEF_DESCRIPTION}

## Z-ZOA Architectural Standards

This skill complies with the Z-ZOA Calculation Room scientific rules:
1. **Provenance (Rule #1)**: Immutable SHA-256 digests and processing lineage DAGs recorded.
2. **Astropy Units (Rule #2)**: Untyped floats rejected; all physical quantities use `astropy.units.Quantity`.
3. **Cosmology Lock (Rule #3)**: Uses standard cosmological parameters ($H_0 = 74.6\text{ km s}^{-1}\text{Mpc}^{-1}$, $\Omega_m = 0.3$, $\Omega_\Lambda = 0.7$).
4. **Holdout Defense (Rule #4)**: No direct access to `datasets/HOLDOUT/` without passing through the cryptographic `reveal_gate`.

## Dependencies

{DEPENDENCIES_LIST}

## Quick Start

```powershell
uv run scripts/{SCRIPT_NAME}.py run --output runs/{SKILL_NAME}_results.json
```

## Utility Scripts

The skill provides helper scripts in `scripts/`:

### `scripts/{SCRIPT_NAME}.py`

- `run`: Executes the main workflow task.
- `verify`: Checks output integrity and generates summary manifests.

## Error Handling & Safeguards

- **Fail-Fast**: Exits immediately on error with code 1.
- **Holdout Boundary**: Raises `HoldoutLeakageViolationError` if holdout data is accessed inappropriately.
- **File Output Standard**: Structured results are written to JSON files; terminal output is concise.

## Common Mistakes

- Failing to wrap numerical quantities in `astropy.units`.
- Attempting to read holdout datasets during model tuning.
- Emitting unparsed raw data directly to terminal stdout.
