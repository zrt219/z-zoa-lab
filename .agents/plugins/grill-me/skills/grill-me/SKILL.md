---
name: grill-me
description: >-
  Executes the inviolable /grill-me interview protocol and verifies exact fidelity
  of the Z-ZOA Calculation Room and 3D Lab Companion against the 10-sheet research plan in main plan/.
---

# /grill-me Protocol & Z-ZOA 10-Sheet Verification Skill

## Overview
This skill operationalizes the inviolable requirement that the agent never divert from the `/grill-me` alignment interview protocol, and guarantees that the Z-ZOA research workbench and 3D Lab Room permanently preserve the exact scientific functionality and aesthetic designed in the 10 sheets in `main plan/`.

## The Inviolable /grill-me Protocol
1. **Never Divert**: Whenever `/grill-me` or an alignment interview is requested, do not rush to coding or planning without completing the interview.
2. **One Question at a Time**: Use the `ask_question` tool with strictly **one question per call**.
3. **Research First**: Before presenting questions, explore existing codebase files, schemas, and configurations.
4. **Actionable Options**:
   - Provide 2–4 options written as direct user responses.
   - Always prefix your top recommended option with `(Recommended)`.
   - Do NOT include an "Other" option (the UI provides write-in by default).

## The 10-Sheet Architectural Reference (`main plan/`)
Whenever reviewing, building, or modifying features, cross-reference these 10 sheets:
- **Page 1 (The Big Picture)**: 10-phase research lifecycle from scientific question to paper submission.
- **Page 2 (What We Download)**: Official catalogues (CF4, 2MRS, HIZOA, MeerKAT holdouts). Immutable raw data, SHA-256 manifests.
- **Page 3 (White Calculation Room v0.1)**:
  - 5 tabs: `Experiment`, `Data`, `Cosmology`, `Calculation`, `Run Manifest`.
  - 4-quadrant layout with parameters, quick equations, sample outputs preview table, terminal logs, and manifest YAML.
- **Page 4 (3D Lab Companion)**:
  - Stylized Three.js WebGL canvas matching the notebook sketch look (`#FAF8F5`).
  - Layers: H I point clouds, CF4 velocity field arrows, Milky Way obscuration plane ($|b| < 10^\circ$), cosmic streamlines, galaxy markers, 3D grid/axes, annotations.
  - Controls: Orbit/pan/zoom, dual-axis slice depth clipping plane slider, camera presets, click-to-inspect galaxy card.
- **Page 5 (Leakage Protection)**: Holdout Guard: ARMED/LOCKED, 7-step leakage workflow, 12-test audit suite.
- **Page 6 (Baseline Science Checks)**: Astropy units, Supergalactic coordinate rotations, cosmology presets, mock universe testing.
- **Page 7 (Reconstruction Engine)**: Wiener filter + ~200 constrained realizations, mean field $\langle\delta\rangle$, sigma field $\sigma$, overdensity probability $P(\delta > 0)$.
- **Page 8 (Freeze -> Reveal -> Score)**: Sealed prediction token, holdout unsealing, 1,000-run null distribution, empirical Z-score ($z = 4.77\sigma$), p-value.
- **Page 9 (Hybrid + Integrity)**: MeerKAT hybrid delta comparison, XRPL Testnet notarization pipeline and receipts.
- **Page 10 (From Results to Paper)**: In-browser LaTeX/Markdown manuscript editor, publication figures, pre-submission checklist, CLI packager, 1-click bundle download (.ZIP).

## Verification Commands
To ensure all contracts are satisfied:
```powershell
# Backend test suite (all 63 tests must pass)
.venv\Scripts\pytest tests -v

# Frontend build & typecheck (0 errors)
cd frontend
pnpm run build
pnpm run lint
```
