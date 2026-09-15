# Z-ZOA Calculation Room: Phase 1 Architecture & Design Specification

**Document Version**: 1.0.0  
**Project**: Z-ZOA Calculation Room (`z-zoa-lab`)  
**Mission**: "Z-ZOA: Out-of-Sample Reconstruction and H I Validation of Large-Scale Structure Across the Galactic Zone of Avoidance"  
**Scope**: Phase 1 Foundation — Architecture, Units, Coordinates, Cosmology, Provenance, Holdout Protection, Manifests, and Quiet White Calculation UI.

---

## 1. System Philosophy & Architecture

### 1.1 Decoupling Visualization from Calculation
The Z-ZOA Calculation Room is deliberately decoupled from exploratory 3D visualization tools (such as `blissful-galileo`). While visualization tools are intended for sensory exploration of the cosmic web, the Calculation Room is a scientific workbench designed for **numerical precision, strict data provenance, uncertainty propagation, out-of-sample holdout protection, and absolute reproducibility**.

The system is structured as three isolated layers:
1. **Scientific Core (`research/`)**: Pure Python 3.12+ scientific engine. It has zero dependency on web frameworks, frontends, or visualization layers. It can be executed via CLI, Jupyter, or imported into automated batch pipelines.
2. **API Layer (`backend/`)**: A lightweight FastAPI service that exposes the scientific core over typed REST endpoints. It enforces execution context (Training vs. Validation mode) and logs all calculation invocations.
3. **Calculation Console (`frontend/`)**: A minimalist, high-contrast, quiet white UI built with React, Vite, and TypeScript. It evokes a quiet white scientific laboratory / research notebook. It contains no 3D scenes, no WebGL, no particles, and no marketing chrome.

```
+-------------------------------------------------------------------------------+
|                       Z-ZOA CALCULATION ROOM (Frontend)                       |
|   Quiet White Workstation UI (React + TypeScript + Vite + Tailwind/CSS)       |
+---------------------------------------+---------------------------------------+
                                        | (HTTP / JSON-RPC / SSE)
+---------------------------------------v---------------------------------------+
|                         BACKEND API SERVICE (backend/)                        |
|   FastAPI Application: Execution Contexts, Manifest Registry, RPC Gateway     |
+---------------------------------------+---------------------------------------+
                                        | (Direct Python In-Process)
+---------------------------------------v---------------------------------------+
|                         SCIENTIFIC ENGINE (research/)                         |
|  +-------------------+  +--------------------+  +--------------------------+  |
|  | units & constants |  | coordinates & frame|  | cosmology & distances    |  |
|  +-------------------+  +--------------------+  +--------------------------+  |
|  +-------------------+  +--------------------+  +--------------------------+  |
|  | peculiar velocity |  | catalog registry   |  | holdout guard & boundary |  |
|  +-------------------+  +--------------------+  +--------------------------+  |
|  +-------------------+  +--------------------+  +--------------------------+  |
|  | provenance tracker|  | run manifests      |  | validation kernels       |  |
|  +-------------------+  +--------------------+  +--------------------------+  |
+---------------------------------------+---------------------------------------+
                                        |
+---------------------------------------v---------------------------------------+
|                           IMMUTABLE DATA REPOSITORY                           |
|  datasets/raw/ (TRAIN)  |  datasets/HOLDOUT/ (LOCKED)  |  datasets/reference/ |
+-------------------------------------------------------------------------------+
```

---

## 2. Phase 1 File Tree

```
z-zoa-lab/
├── .gitignore
├── pyproject.toml
├── uv.lock
├── README.md
├── docs/
│   └── design/
│       └── PHASE_1_DESIGN.md
├── datasets/
│   ├── raw/
│   │   ├── cf4/
│   │   │   ├── SOURCE.md
│   │   │   └── sha256.txt
│   │   ├── 2mrs/
│   │   │   ├── SOURCE.md
│   │   │   └── sha256.txt
│   │   └── hizoa/
│   │       ├── SOURCE.md
│   │       └── sha256.txt
│   ├── HOLDOUT/
│   │   ├── vela_smgps/
│   │   │   ├── SOURCE.md
│   │   │   └── sha256.txt
│   │   ├── vela_hi/
│   │   │   ├── SOURCE.md
│   │   │   └── sha256.txt
│   │   └── ga_smgps/
│   │       ├── SOURCE.md
│   │       └── sha256.txt
│   ├── reference/
│   │   ├── cf4_grids/
│   │   │   ├── SOURCE.md
│   │   │   └── sha256.txt
│   │   ├── cf4pp/
│   │   │   ├── SOURCE.md
│   │   │   └── sha256.txt
│   │   └── wallaby_dr2/
│   │       ├── SOURCE.md
│   │       └── sha256.txt
│   ├── processed/
│   └── manifests/
├── references/
│   ├── CF4/
│   ├── 2MRS/
│   ├── HIZOA/
│   ├── Vela-SMGPS/
│   ├── Vela-HI/
│   ├── GA-SMGPS/
│   └── WALLABY/
├── research/
│   ├── __init__.py
│   ├── units/
│   │   ├── __init__.py
│   │   └── validation.py
│   ├── coordinates/
│   │   ├── __init__.py
│   │   ├── frames.py
│   │   └── transforms.py
│   ├── cosmology/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   └── distances.py
│   ├── velocities/
│   │   ├── __init__.py
│   │   ├── peculiar.py
│   │   ├── frames.py
│   │   └── uncertainties.py
│   ├── catalogs/
│   │   ├── __init__.py
│   │   ├── schema.py
│   │   ├── registry.py
│   │   ├── loader.py
│   │   └── decontaminate.py
│   ├── holdouts/
│   │   ├── __init__.py
│   │   ├── guard.py
│   │   └── exceptions.py
│   ├── provenance/
│   │   ├── __init__.py
│   │   ├── tracker.py
│   │   └── models.py
│   └── experiments/
│       ├── __init__.py
│       ├── context.py
│       ├── manifest.py
│       └── runner.py
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── calculation.py
│   │   ├── catalogs.py
│   │   ├── experiments.py
│   │   └── health.py
│   └── schemas/
│       ├── __init__.py
│       └── api_models.py
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── index.html
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── index.css
│   │   ├── components/
│   │   │   ├── Header.tsx
│   │   │   ├── ExperimentBanner.tsx
│   │   │   ├── CatalogRegistryView.tsx
│   │   │   ├── CalculationConsole.tsx
│   │   │   ├── ManifestInspector.tsx
│   │   │   └── ProvenanceChainView.tsx
│   │   ├── types/
│   │   └── services/
│   │       └── api.ts
├── runs/
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_units.py
    ├── test_coordinates.py
    ├── test_cosmology.py
    ├── test_velocities.py
    ├── test_catalogs.py
    ├── test_holdout_guard.py
    ├── test_provenance.py
    └── test_reproducibility.py
```

---

## 3. Scientific Dependency Choices & Rationale

| Dependency | Version | Role in Z-ZOA | Scientific Justification |
| :--- | :--- | :--- | :--- |
| **Python** | `>=3.12` | Runtime Language | Strict typing improvements, performance gains, long-term support for research lifecycle (2025–2030). |
| **Astropy** | `>=6.1` | Units, Cosmology, Coordinates | Gold-standard astronomy library. Prevents rolling custom spherical trigonometry, precession, IAU frame conversions, or cosmological Friedmann solvers. Astropy coordinates are verified against USNO/IAU standards. |
| **NumPy** | `>=2.0` | Numerical Core | Foundation for array operations, vector arithmetic, linear algebra. |
| **SciPy** | `>=1.14` | Scientific Numerics | Quadrature integration (cosmological distance integrals), statistical distributions, interpolation. |
| **Polars** & **PyArrow** | `>=1.6` / `>=17.0` | Columnar Data Processing | Fast, zero-copy, memory-efficient columnar formats for handling catalogues (CF4: 55,877 rows; 2MRS: 44,599 rows). Guarantees immutable columnar semantics and native Parquet read/write. |
| **Pydantic** | `>=2.8` | Schema Validation & Serialization | Cryptographically reproducible serialization of run configurations, dataset schemas, manifest JSONs, and API models. |
| **FastAPI** & **Uvicorn** | `>=0.115` / `>=0.30` | Minimal REST Gateway | Fast, typed, self-documenting asynchronous RPC interface bridging the Python calculation core to the frontend. |
| **pytest** & **pytest-cov** | `>=8.3` | Test Verification | Automated scientific verification framework checking calculations against published reference standards. |
| **React** & **TypeScript** | `^18.3` / `^5.5` | Frontend Interface | Type-safe user interface implementation for the quiet white calculation workstation. |
| **Vite** | `^5.4` | Build Tooling | Sub-second HMR and deterministic production bundling for the frontend. |

---

## 4. Enforcement of Units and Provenance

### 4.1 Strict Unit Enforcement
1. **Astropy Units as Internal Standard**:
   - Within `research/`, all physical quantities (distances, velocities, angles, expansion rates) must be instances of `astropy.units.Quantity`.
   - Naked floats or untyped numerical values passed into core calculation kernels will trigger an immediate `UnspecifiedUnitError`.
2. **Interface Boundaries**:
   - Any external input (API request, config YAML, JSON payload) must provide both `value` (float or list of floats) and `unit` (e.g., `"Mpc"`, `"km / s"`, `"deg"`, `"km s-1 Mpc-1"`).
   - Pydantic models automatically validate unit strings against Astropy's unit registry.
3. **Serialization**:
   - Manifests and results store explicit pairs:
     ```json
     {
       "quantity": "peculiar_velocity",
       "value": 472.312,
       "unit": "km / s",
       "uncertainty": {
         "value": 38.45,
         "unit": "km / s",
         "confidence_level": 0.6827
       }
     }
     ```

### 4.2 Immutable Provenance
1. **Raw Catalog Immutability**:
   - Files in `datasets/raw/` and `datasets/HOLDOUT/` are read-only.
   - Every file must have an accompanying `sha256.txt`. The loader computes the SHA-256 upon reading; if it does not match, execution halts with `ChecksumMismatchError`.
2. **Lineage DAG**:
   - Every computation node records:
     - `node_id`: UUIDv4
     - `step_name`: Canonical function name (e.g., `research.velocities.peculiar.calculate_peculiar_velocity`)
     - `git_commit`: Current commit hash (or dirty flag with diff summary)
     - `inputs`: Map of parameter names to values, units, and parent node IDs
     - `formula`: Exact mathematical relationship formatted in LaTeX and plain text
     - `reference_frame`: Velocity / coordinate reference frame (e.g., `CMB_FRAME`, `HELIOCENTRIC`, `SUPERGALACTIC`)
     - `outputs`: Output quantities with units and propagated uncertainties
3. **Run Manifest**:
   - On completion, an experiment run writes an atomic `manifest.json` under `runs/{run_id}/` containing the full environment signature (package versions, OS, git commit, random seed, dataset checksums, and execution DAG).

---

## 5. Technical Holdout Protection (Leakage Defense)

Preventing accidental leakage of holdout catalogues (e.g. `Vela-SMGPS` and `Vela-HI`) into training and reconstruction tuning is paramount. An "honor system" is scientifically insufficient.

### 5.1 RBAC Dataset Categorization
Every dataset in the registry is tagged with a mandatory role:
- `Role.TRAIN`: Permitted in training, reconstruction, calibration, and validation.
- `Role.HOLDOUT`: **Prohibited** during training/reconstruction. Permitted **only** during post-freeze validation.
- `Role.COMPARISON_ONLY`: Reference fields (e.g. CF4 official grids); prohibited from model fitting.

### 5.2 Context-Gated Data Gateway
Direct disk reads (e.g., arbitrary `open()` or `polars.read_parquet()` of holdout paths) by experiment code are prohibited by architecture. All access must proceed through `DataGateway.load_catalog(dataset_id: str, context: ExecutionContext)`.

```python
class ExecutionMode(Enum):
    TRAINING = "training"
    VALIDATION = "validation"
    AUDIT = "audit"

class DataGateway:
    def load_catalog(self, dataset_id: str, context: ExecutionContext) -> Table:
        catalog_meta = self.registry.get(dataset_id)
        
        if catalog_meta.role == DatasetRole.HOLDOUT:
            if context.mode == ExecutionMode.TRAINING:
                raise HoldoutLeakageViolationError(
                    f"[SECURITY VIOLATION] Attempted to access HOLDOUT dataset '{dataset_id}' "
                    f"within TRAINING context '{context.run_id}'. "
                    f"Holdout catalogues are strictly isolated until reconstruction is frozen."
                )
            if context.mode == ExecutionMode.VALIDATION:
                if not context.is_frozen_manifest_present():
                    raise UnfrozenValidationViolationError(
                        f"[SECURITY VIOLATION] Attempted to unlock HOLDOUT dataset '{dataset_id}' "
                        f"without a cryptographically sealed training run manifest."
                    )
        return self._read_and_verify_table(catalog_meta)
```

### 5.3 Cryptographic Sealing Protocol
1. An experiment is first executed in `ExecutionMode.TRAINING` using only `TRAIN` datasets.
2. When training finishes, a `manifest.json` is generated and cryptographically hashed (`manifest_sha256`). The model weights/density grid/velocity field output is sealed and marked `FROZEN`.
3. Validation mode requires passing this `frozen_manifest_sha256`. The validation engine records both the frozen training hash and the holdout dataset hash in the validation report.
4. If any parameter in the training pipeline is changed, the seal breaks, and validation results are invalidated.

---

## 6. First Automated Scientific Tests

The test suite in `tests/` tests real astronomy numerical values against established references:

1. **Coordinate Frame Transformations (`test_coordinates.py`)**:
   - **Galactic Center Verification**: Verify $(l=0^\circ, b=0^\circ)$ transforms to ICRS $(\alpha \approx 266.405^\circ, \delta \approx -28.936^\circ)$ matching IAU standard definitions.
   - **Supergalactic Plane**: Verify known points on the Supergalactic equator transform to $SGB = 0^\circ$ within $10^{-6}$ degrees.
   - **Cartesian Invertibility**: Transform spherical $(RA, Dec, d) \leftrightarrow (X, Y, Z)$ across 10,000 synthetic test points and assert recovery to $< 10^{-12}$ relative tolerance.
2. **Cosmological Distance Measures (`test_cosmology.py`)**:
   - **FLRW Integration**: Test Flat $\Lambda$CDM distance functions ($d_C, d_L, d_A$) at $z \in [0.001, 0.05, 0.1, 1.0]$ against pre-calculated Astropy `Planck18` and `WMAP9` benchmarks.
   - **Distance Modulus**: Verify $\mu = 5 \log_{10}(d_L / 10\text{ pc})$ and its exact inverse $d_L(\mu) = 10^{(\mu/5)+1}\text{ pc}$.
   - **Hubble Parameter**: Verify $H(z) = H_0 \sqrt{\Omega_{m,0}(1+z)^3 + \Omega_{\Lambda,0}}$.
3. **Peculiar Velocities & Frames (`test_velocities.py`)**:
   - **Low-z Linear Estimator**: $v_{\rm pec} = c z - H_0 d$ with measurement errors $\sigma_z, \sigma_d, \sigma_{H_0}$. Verify analytical propagation of variance $\sigma_{v_{\rm pec}}^2$.
   - **CMB Dipole Frame Correction**: Test conversion from Heliocentric to CMB frame using the standard CMB dipole vector ($v_{\rm apex} = 369.82\text{ km/s}, l=264.021^\circ, b=48.253^\circ$).
4. **Holdout Guard & Leakage Defense (`test_holdout_guard.py`)**:
   - Test that calling `load_catalog('vela_smgps')` under `TRAINING` context raises `HoldoutLeakageViolationError`.
   - Test that directory traversal or raw path spoofing fails safely.
   - Test that `VALIDATION` mode succeeds *only* when accompanied by a valid frozen manifest.
5. **Reproducibility & Manifest Replay (`test_reproducibility.py`)**:
   - Run a multi-step calculation $\to$ write `runs/test_run/manifest.json`.
   - Reload the manifest $\to$ rerun identical calculation $\to$ assert exact bit-for-bit numerical identity.
   - Modify a parameter in the config $\to$ assert that integrity verification catches the change.

---

## 7. Refinements & Constructive Scientific Critique of the Specification

Before implementation, we identify the following critical scientific and technical refinements:

1. **Peculiar Velocity Estimator Formulation at Non-Zero Redshift**:
   - *Issue*: The simple formula $v_{\rm pec} \approx c z - H_0 d$ breaks down as redshift increases (even at $cz \sim 6,000 - 15,000\text{ km/s}$, cosmological expansion effects become noticeable, and $cz$ is not pure recession velocity).
   - *Refinement*: Implement two distinct estimators:
     a. `LinearPeculiarVelocityEstimator`: $v_{\rm pec} = c z - H_0 d$ (strictly flagged as low-$z$ exploratory approximation).
     b. `CosmologicalPeculiarVelocityEstimator`: Using $(1 + z_{\rm obs}) = (1 + z_{\rm cos})(1 + z_{\rm pec})$, where $z_{\rm cos}$ is inverted from the cosmological distance $d_C(z_{\rm cos}) = d$, yielding $v_{\rm pec} = c \frac{(1+z_{\rm pec})^2 - 1}{(1+z_{\rm pec})^2 + 1} \approx c z_{\rm pec}$.
2. **Log-Normal Distance Errors**:
   - *Issue*: In Cosmicflows-4, galaxy distances are derived from distance moduli $\mu = m - M$. Uncertainties are symmetric in $\mu$ ($\sigma_\mu$), which implies asymmetric log-normal uncertainties in linear distance $d$:
     $$\sigma_d^+ = d (10^{\sigma_\mu / 5} - 1), \quad \sigma_d^- = d (1 - 10^{-\sigma_\mu / 5})$$
   - *Refinement*: Store and propagate $\sigma_\mu$ directly. For peculiar velocity uncertainty, use:
     $$\sigma_v \approx \frac{\ln(10)}{5} H_0 d \sigma_\mu \approx 0.4615 \cdot H_0 d \cdot \sigma_\mu$$
     This avoids artificial skew from naive symmetric linear distance approximations.
3. **Automated Cross-Match & Decontamination for HIZOA**:
   - *Issue*: HIZOA-S contains 39 sources that overlap with the Vela-SMGPS holdout footprint. Dumping HIZOA directly into training would cause subtle data leakage into the reconstruction.
   - *Refinement*: Build an explicit `CatalogDecontaminator` module in Phase 1 that performs sky-coordinate and velocity separation matching against holdout catalogues, generating a cleaned `hizoa_decontaminated` product with audit logs.
4. **Minimal Quiet White Interface Architecture**:
   - *Refinement*: The UI will be built as a single-page calculation workspace using clean monospace typography (`JetBrains Mono` / `SF Mono` / `Consolas`), 1px borders (`#E5E7EB`), pure white background (`#FFFFFF`), and no decorative cards. It presents live data tables, mathematical LaTeX equations, provenance trees, and holdout lock indicators.

---

## 8. Approval Checklist for Implementation

- [x] Architectural separation approved (no 3D/WebGL visualizer; pure scientific workbench).
- [x] Phase 1 file tree specified down to individual modules.
- [x] Dependencies selected and justified (`astropy`, `numpy`, `scipy`, `polars`, `pydantic`, `fastapi`, `react`, `vite`).
- [x] Unit enforcement and provenance DAG mechanisms designed.
- [x] Holdout boundary RBAC and cryptographic freeze protocol designed.
- [x] Automated test plan defined with real astronomical benchmark values.
- [x] Scientific refinements (relativistic peculiar velocity, $\sigma_\mu$ log-normal error, HIZOA decontamination) incorporated.
