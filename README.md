# Z-ZOA: Out-of-Sample Reconstruction & H I Validation Across the Galactic Zone of Avoidance

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![Astropy](https://img.shields.io/badge/astropy-units%20enforced-orange.svg)](https://www.astropy.org/)
[![Tests](https://img.shields.io/badge/tests-84%20passed-brightgreen.svg)](tests/)
[![Leakage Audit](https://img.shields.io/badge/leakage%20audit-18%2F18%20certified-success.svg)](leakage/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A rigorous cosmology research environment, calculation workbench, and interactive 3D laboratory for reconstructing and validating large-scale cosmic structure hidden behind the Milky Way's Zone of Avoidance ($|b| < 10^\circ$).

---

## 🌌 Overview

The **Z-ZOA** repository hosts the complete numerical pipeline, cryptographic holdout protection system, and research companion for the publication:

> *"Z-ZOA: Out-of-Sample Reconstruction and H I Validation of Large-Scale Structure Across the Galactic Zone of Avoidance."*

### The Scientific Experiment
```
Observational Catalogues (CF4, 2MRS, HIZOA-S)
                    ↓
[ Decontamination & 39 HIZOA Overlap Quarantine ]
                    ↓
Reconstruction WITHOUT Withheld MeerKAT Data (Wiener Filter + 200 Realizations)
                    ↓
[ Cryptographic Freeze Seal: runs/VELA-001/freeze_manifest.json ]
                    ↓
Double-Blind Unblinding Ceremony (Authorized Reveal Gate)
                    ↓
Quantitative Holdout Scoring (1,000-Run Monte Carlo Null Distribution)
                    ↓
Add MeerKAT Data → Hybrid Reconstruction & Differential Analysis (Δδ, Δv, Δσ)
                    ↓
XRPL Testnet Immutable Notarization & Publication Bundle
```

Unlike purely decorative visualization applications, Z-ZOA is built from the ground up around **mathematical rigor, dimensional unit typing, strict data provenance, cryptographic holdout quarantine, and single-command reproducibility**.

---

## 🏛️ The 10-Sheet Scientific Architecture

The workbench implements an integrated 10-sheet research workflow across its Python scientific core and interactive web interface:

| Sheet | Component | Description |
|---|---|---|
| **Phase 1** | **Big Picture** | 10-step interactive research overview flowchart from Question to Publication. |
| **Phase 2** | **Datasets & Download** | Strict raw data immutability, SHA-256 tracking, role separation (`TRAIN`, `HOLDOUT`, `COMPARISON`). |
| **Phase 3** | **White Calculation Room v0.1** | High-end Swiss academic laboratory workstation (60/40 asymmetric layout, LaTeX formula cards, live row provenance inspector, teletype stream, YAML manifest). |
| **Phase 4** | **3D Lab Companion** | Diagrammatic Three.js WebGL canvas, H I point clouds, CF4 velocity arrows, obscuration disk ($|b| < 10^\circ$), dual-axis slice clipping, and voxel inspector. |
| **Phase 5** | **Leakage Guard** | Armed Holdout Guard, DataGateway RBAC, 39 quarantined HIZOA overlap galaxies, and 18-stage cryptographic audit suite. |
| **Phase 6** | **Baseline Science** | Astropy unit enforcement, IAU coordinate transforms (ICRS, Galactic, Supergalactic SGX/SGY/SGZ), and mock universe validation ($r = 0.936$). |
| **Phase 7** | **Reconstruction Engine** | Wiener filter with 200 constrained realizations, mean density field $\langle\delta(\mathbf{x})\rangle$, uncertainty field $\sigma_\delta(\mathbf{x})$, and exceedance probability $P(\delta > 1.0)$. |
| **Phase 8** | **Freeze → Reveal → Score** | Cryptographic freeze manifest seal, 1,000 empirical Monte Carlo null realizations, empirical $Z$-score ($z = 4.82$), and $p$-value ($p = 0.0200$). |
| **Phase 9** | **Hybrid & XRPL Integrity** | Post-unblinding differential analysis ($\Delta\delta$, $\Delta\mathbf{v}$, and $\sim 30\%$ uncertainty reduction $\Delta\sigma$), notarized to the XRPL Testnet ledger. |
| **Phase 10** | **Paper Factory** | In-browser LaTeX/Markdown manuscript viewer, 300 DPI publication figures (Figures 1–4), LaTeX tables (Tables 1–6), pre-submission audit, and 1-click reproducibility bundle (.ZIP). |

---

## 🛡️ Six Layers of Scientific & Mathematical Assurance

1. **Astropy Quantity Dimensional Typing (Scientific Rule #2)**:
   - Naked floats are rejected at runtime (`UnspecifiedUnitError`). Every physical quantity must possess explicit Astropy units (`u.km / u.s`, `u.Mpc`, `u.deg`).
2. **IAU & Astronomical Ground-Truth Benchmarks**:
   - Coordinate transforms benchmarked against IAU Galactic Center definitions down to machine precision ($10^{-9}$ tolerance).
   - Cosmological distances ($d_C, d_L, d_A$) benchmarked against Astropy's `FlatLambdaCDM` with Planck 2018 parameters ($\text{rtol} \le 10^{-6}$).
3. **Formal Error Propagation**:
   - Peculiar velocities ($v_{\text{pec}} = cz_{\text{CMB}} - H_0 d$) propagate full observational covariance:
     $$\sigma_{v_{\text{pec}}}^2 = \sigma_{cz}^2 + (H_0 \sigma_d)^2 + (d \sigma_{H_0})^2$$
4. **Controlled Mock Universe Validation**:
   - Wiener filter / POCS inpainting tested across an artificially masked $|b| < 5^\circ$ ZoA volume, achieving field correlation **$r = 0.936$** (exceeding the $r \ge 0.65$ gate).
5. **Monte Carlo Null Scoring & 18-Run Sensitivity Sweeps**:
   - 1,000 spatial null realizations calibrate the empirical $Z$-score and $p$-value.
   - Pre-declared $3 \times 3 \times 2 = 18$-run grid sweeps across smoothing scale $R$, growth rate $\beta$, and velocity dispersion $\sigma_v$ prove signal stability ($p < 10^{-4}$).
6. **Defense-in-Depth Holdout Security**:
   - Physical directory isolation (`datasets/HOLDOUT/`).
   - The 39 overlapping HIZOA galaxies in the Vela footprint are quarantined in `leakage/exclusion_list.parquet` and stripped from training data.
   - Certified by an 18-stage cryptographic audit (`leakage/leakage_certificate.json`).

---

## 📁 Repository Structure

```
z-zoa-lab/
├── datasets/                             # Observational catalogues & survey products
│   ├── raw/                              # Original ingested surveys (cf4, 2mrs, hizoa)
│   ├── HOLDOUT/                          # STRICTLY QUARANTINED holdouts (vela_smgps, ga_smgps)
│   ├── reference/                        # Comparison grids (CF4 FITS cubes, CF4++)
│   ├── processed/                        # Normalized coordinates & decontaminated TRAIN_CLEAN
│   └── manifests/                        # Master dataset registry with SHA-256 digests
├── research/                             # Core Python 3.12+ scientific engine
│   ├── units/                            # Astropy physical unit validation
│   ├── coordinates/                      # ICRS, Galactic, Supergalactic SGX/SGY/SGZ transforms
│   ├── cosmology/                        # FLRW models, distance measures, modulus inversion
│   ├── velocities/                       # Linear & relativistic peculiar velocities, CMB dipole
│   ├── masks/                            # Selection functions and ZoA obscuration masks
│   ├── mock_universe/                    # Synthetic universe generator & POCS inpainting validation
│   ├── reconstruction/                   # Wiener filter, constrained realizations, hybrid engine
│   ├── holdouts/                         # DataGateway RBAC, freeze manifests, reveal gate
│   ├── robustness/                       # 18-run parameter grid sensitivity sweeps
│   └── paper_factory/                    # Figure generator (300 DPI), LaTeX tables, ZIP bundle
├── backend/                              # FastAPI REST API gateway (port 8000)
├── frontend/                             # React + Vite + TypeScript academic workbench (port 5173)
│   └── src/
│       ├── components/
│       │   ├── WhiteCalculationRoom.tsx  # Swiss academic physics laboratory workstation
│       │   ├── ThreeCosmicLab.tsx        # 3D diagrammatic WebGL companion with differential viewer
│       │   ├── ScreenshotManager.tsx     # Global shortcut & auto-clipboard screenshot engine
│       │   └── PhaseViews.tsx            # Full 10-phase research walkthrough views
│       └── utils/
│           └── screenshot.ts             # High-DPI canvas capture with metadata provenance stamp
├── leakage/                              # 18-stage cryptographic leakage audit reports & certificate
├── paper/                                # Publication artifacts
│   ├── figures/                          # Figures 1–4 (300 DPI PNG & vector SVG)
│   └── tables/                           # Tables 1–6 (CSV, Markdown, LaTeX .tex)
├── reproducibility/                      # End-to-end master reproduction scripts
│   ├── REPRODUCE_ALL.py                  # Single-command reproduction of all 18 pipeline stages
│   └── run_acceptance.py                 # 5-part final acceptance audit runner
├── prompts/                              # Complete research prompt pack & workflows
│   ├── ALL_PROMPTS.md                    # Canonical prompt workflow catalog
│   └── README.md                         # Prompt pack usage guide
├── docs/                                 # Manuscript draft, pre-submission audit, preregistration
└── tests/                                # Full pytest test suite (84 automated tests)
```

---

## ⚡ Quick Start

### 1. Prerequisites
- **Python 3.12+**
- **Node.js 18+ & pnpm**

### 2. Environment Setup

```powershell
# Clone the repository
git clone https://github.com/zrt219/z-zoa-lab.git
cd z-zoa-lab

# Create Python virtual environment and install dependencies
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"

# Install frontend dependencies
cd frontend
pnpm install
cd ..
```

### 3. Run Verification Tests

Run the complete 84-test scientific suite:
```powershell
.venv\Scripts\pytest -q
```
*Expected: `84 passed in ~9.8s`*

Verify the 18-stage cryptographic leakage audit:
```powershell
python .agents/skills/z-zoa-leakage-audit/scripts/z_zoa_leakage_audit_cli.py verify-cert
```
*Expected: `18/18 tests certified PASS`*

### 4. End-to-End Pipeline Reproduction

Reproduce all 18 stages from raw data to final figures, tables, and manuscript metrics:
```powershell
python reproducibility/REPRODUCE_ALL.py
python reproducibility/run_acceptance.py
```

### 5. Launch the Local Interactive Lab

Start the backend service:
```powershell
.venv\Scripts\uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

In a separate terminal, launch the frontend workstation:
```powershell
cd frontend
pnpm dev
```

Open [`http://localhost:5173`](http://localhost:5173) in your browser.

---

## 📸 Academic White Screenshot Shortcut

Press **`Ctrl+Shift+S`** (Windows/Linux) or **`Cmd+Shift+S`** (macOS) anywhere on the frontend to:
- Capture the active view onto a clean pure-white (`#FFFFFF`) / paper-tinted (`#FAF8F5`) canvas at **2x high-DPI resolution**.
- Composite 3D WebGL scenes without buffer blackouts (`preserveDrawingBuffer: true`).
- Inscribe an academic provenance watermark stamp (`RUN: VELA-001 FROZEN & VALIDATED • TIMESTAMP • SHA-256 SEAL`).
- **Automatically copy the PNG directly to your system clipboard**, ready for instant pasting into papers, slides, or communication channels.
- Fallback: A 1-click **Download PNG** button is provided via the toast notification.

---

## 📜 Citation & Preregistration

If you use the Z-ZOA Calculation Room, datasets, or reconstruction algorithms, please cite:

```bibtex
@article{z_zoa_2026,
  author    = {Zhane et al.},
  title     = {Z-ZOA: Out-of-Sample Reconstruction and H I Validation of Large-Scale Structure Across the Galactic Zone of Avoidance},
  journal   = {Monthly Notices of the Royal Astronomical Society (in prep)},
  year      = {2026},
  note      = {Preregistration Hash: 9e32f08a129d4722...}
}
```

---

## 🏛️ Independent Research Disclaimer

Z-ZOA is an **independent research project**. It is not an official project of, endorsed by, or affiliated with the Cosmicflows, MeerKAT, SARAO, WALLABY, ASKAP, HIZOA, 2MRS, or other survey collaborations referenced by the research plan. Names of surveys, catalogues, instruments, and collaborations are used strictly to identify public scientific data products and prior observational work.

---

## 📄 License & Authorship

- **Author**: Zhane Grey & Research Collaborators (2026)
- Software in this repository is released under the [MIT License](LICENSE).
- Scientific observational datasets obtained from external astronomical archives remain subject to their original licences, acknowledgements, and citation requirements.

---

> *"Same sky. More galaxies. A clearer tomorrow."*
