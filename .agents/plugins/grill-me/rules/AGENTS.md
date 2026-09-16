# Inviolable Rules: /grill-me Protocol & 10-Sheet Architecture Contract

## 1. The /grill-me Invariant (Written in Stone)
When the user invokes `/grill-me` or requests an architectural design interview:
1. **NEVER divert, shortcut, or batch questions**: You must walk down each branch of the design tree, resolving dependencies one by one.
2. **One Question at a Time**: Always ask questions strictly ONE AT A TIME using the `ask_question` tool. Never present multi-question dumps in text or in a single tool call.
3. **Explore Codebase First**: If a question can be answered by exploring files or running read commands, explore the codebase instead of asking.
4. **Always Provide Recommended Answer**: Every question must include a clear option prefixed with `(Recommended)`.
5. **Format Options as User Responses**: Each option should be written from the user's perspective.

## 2. The 10-Sheet Z-ZOA Research & 3D Lab Contract
All future modifications to `Z-zoa-lab` must preserve the exact functionality and aesthetics established in `main plan/`:
- **Phase 1: Big Picture (Page 1)**: 10-step interactive research overview flowchart from Question to Paper.
- **Phase 2: Datasets & Download (Page 2)**: Strict raw data immutability, SHA-256 manifest tracking, role separation (TRAIN vs HOLDOUT vs COMPARISON).
- **Phase 3: White Calculation Room v0.1 (Page 3)**:
  - 5 sub-tabs: `Experiment`, `Data`, `Cosmology`, `Calculation`, `Run Manifest`.
  - Exact 4-quadrant layout: Experiment Setup, Key Parameters ($H_0, \Omega_m, \Omega_\Lambda, v_{\text{CMB}}$, Frame, Units) + Remember Checklist, Quick Equations + Live Sample Outputs preview table, Streaming Terminal Log, and Run Manifest YAML inspector.
- **Phase 4: 3D Lab Companion (Page 4)**:
  - Stylized diagrammatic Three.js WebGL canvas matching the notebook/paper aesthetic (`#FAF8F5`, sketch bounding box).
  - Layers: H I point clouds, CF4 velocity arrows, Milky Way obscuration disk ($|b| < 10^\circ$), cosmic streamlines, galaxy markers, grid/axes, and structure annotations.
  - Controls: Orbit/pan/zoom, dual-axis slice depth clipping plane slider, camera presets, and clickable galaxy inspector.
- **Phase 5: Leakage Guard (Page 5)**: Holdout Guard ARMED/LOCKED status, 7-step leakage workflow, and 12-test audit certificates.
- **Phase 6: Baseline Science (Page 6)**: Coordinate transforms (SGX, SGY, SGZ), Astropy units, cosmology models, and mock universe validation.
- **Phase 7: Reconstruction Engine (Page 7)**: Wiener filter + ~200 constrained realizations, mean field, sigma field, and overdensity probability $P(\delta > 0)$.
- **Phase 8: Freeze -> Reveal -> Score (Page 8)**: Sealed prediction token, 1,000-run Monte Carlo null distribution histogram, empirical Z-score, and p-value calculation.
- **Phase 9: Hybrid & XRPL Integrity (Page 9)**: MeerKAT hybrid delta comparison and immutable XRPL Testnet notarization receipts.
- **Phase 10: Paper Factory (Page 10)**: In-browser LaTeX/Markdown manuscript viewer/editor, publication figures, pre-submission audit, and 1-click Download Reproducibility Bundle (.ZIP).
