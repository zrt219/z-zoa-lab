---
name: z-zoa-skill-creator
description: >-
  Scaffolds and validates new agent skills for the Z-ZOA Calculation Room.
  Enforces strict astronomical provenance, astropy unit typing, cosmology locks,
  holdout boundary isolation, and standardized CLI script interfaces.
---

# Z-ZOA Skill Creator

## Overview

`z-zoa-skill-creator` is a specialized meta-skill engineered for the **Z-ZOA Calculation Room (`z-zoa-lab`)**. It provides standardized scaffolding and automated compliance audits for developing new agent skills that interact with the research laboratory's data, pipelines, and models.

Every skill generated through this tool guarantees compliance with Z-ZOA's core architectural commandments:
1. **Rule #1 — Never Lose Provenance**: Raw files, derived products, and transformations must be anchored by SHA-256 digests and lineage tracking.
2. **Rule #2 — Units Are Not Optional**: Code must use `astropy.units.Quantity` for distances, velocities, and coordinates; bare floats are strictly forbidden.
3. **Rule #3 — Explicit Cosmology**: FLRW parameters ($H_0 = 74.6\text{ km s}^{-1}\text{Mpc}^{-1}$, $\Omega_m = 0.3$, $\Omega_\Lambda = 0.7$) are immutable.
4. **Holdout Boundary Defense**: Protected validation catalogues in `datasets/HOLDOUT/` (e.g. MeerKAT Vela-SMGPS, GA-SMGPS) are strictly isolated and never accessed directly.

## Dependencies

- Python 3.12+ virtual environment (`.venv`) or `uv`.
- `workflow-skill-creator` (foundational distillation framework).

## Quick Start

Scaffold a new skill for catalogue processing with an accompanying CLI script:

```powershell
python .agents/skills/z-zoa-skill-creator/scripts/scaffold_skill.py create `
  --name "z-zoa-wallaby-audit" `
  --description "Audits WALLABY Pilot DR2 comparison catalogues against CF4 coordinates" `
  --with-script
```

Audit an existing skill for Z-ZOA standards compliance:

```powershell
python .agents/skills/z-zoa-skill-creator/scripts/scaffold_skill.py audit `
  --skill-path ".agents/skills/z-zoa-master-workflow"
```

## Utility Scripts

The generator is located at `scripts/scaffold_skill.py`.

### Subcommands

#### 1. `create`
Scaffolds a complete skill directory with frontmatter, structured `SKILL.md`, and optional starter CLI script:
- `--name <str>`: Unique skill identifier (lowercase, hyphens, max 64 characters).
- `--description <str>`: Concise statement of scope and trigger conditions (max 1024 characters).
- `--title <str>`: (Optional) Human-readable skill title.
- `--install-path <path>`: (Optional) Target directory (defaults to `.agents/skills/<name>`).
- `--dependencies <str>`: (Optional) Comma-separated list of required skills.
- `--with-script`: Generates a starter CLI script in `scripts/<name>_cli.py` incorporating unit validation and provenance hashing.
- `--force`: Overwrites existing skill directory if already present.

#### 2. `audit`
Verifies that a skill directory satisfies Z-ZOA quality and safety contracts:
- Validates YAML frontmatter syntax and length limits.
- Inspects documentation for mandatory references to Provenance, Astropy Units, Cosmology, and Holdout defense.
- Checks Python scripts for `--output` structured file redirection.

## Template References

- `references/zoa_skill_template.md`: Canonical markdown template for Z-ZOA skill documentation.
- `references/zoa_script_template.py`: Standard multi-command CLI template enforcing `astropy.units` and SHA-256 provenance.

## Common Mistakes

- **Untyped Scripts**: Writing CLI scripts that take raw floats without unit definitions.
- **Leaking Holdouts**: Generating skills that directly query `datasets/HOLDOUT/` without passing through the cryptographic `reveal_gate`.
- **Large Stdout Dumps**: Printing entire tables or arrays directly to terminal stdout rather than using `--output` JSON files.
