# Z-ZOA Lab

**Independent research software for reconstructing, validating, and studying large-scale structure across the Galactic Zone of Avoidance.**

> **Working paper direction**  
> *Z-ZOA: Out-of-Sample Reconstruction and H I Validation of Large-Scale Structure Across the Galactic Zone of Avoidance*

Z-ZOA Lab is being built around a simple scientific question:

> **How much hidden large-scale structure can be predicted from surrounding public data before deep H I observations are supplied, and how much does the reconstruction change after those observations are added?**

The project is intentionally split into two complementary environments:

- **Calculation Room** — a quiet, reproducible numerical workspace for catalog ingestion, coordinate transforms, cosmology, reconstruction, uncertainty, holdout controls, validation, statistics, and paper outputs.
- **3D Lab Companion** — a supplementary explorer for inspecting the resulting density fields, velocity fields, survey layers, masks, and reconstructed structures. It is not the source of the scientific result; it is a way to inspect it.

The core principle is:

```text
CALCULATE -> FREEZE -> REVEAL -> SCORE -> RECONSTRUCT AGAIN -> PUBLISH
```

---

## Scientific goal

The Zone of Avoidance (ZoA) is not empty. Dust, stars, source confusion, and survey selection effects make parts of the extragalactic sky difficult to observe in optical wavelengths, while radio H I surveys can recover galaxies hidden behind the Galactic plane.

Z-ZOA is designed to combine public peculiar-velocity and redshift information with explicit uncertainty and survey-selection handling to test whether hidden structure can be reconstructed **out of sample**.

The first planned experiment is centered on the Vela region:

```text
TRAINING DATA
    |
    v
reconstruction WITHOUT selected MeerKAT Vela data
    |
    v
freeze model + prediction
    |
    v
cryptographically anchor frozen run
    |
    v
reveal withheld MeerKAT catalogue
    |
    v
score recovery against survey-matched null catalogues
    |
    v
add MeerKAT back in
    |
    v
hybrid reconstruction
    |
    v
measure Delta density / Delta velocity / Delta uncertainty
```

This is deliberately narrower than attempting to reproduce a full state-of-the-art Bayesian cosmological reconstruction on day one.

---

## Planned data layers

The project is designed around public research products including:

| Dataset / product | Planned role | Purpose |
| --- | --- | --- |
| Cosmicflows-4 individual distances | `TRAIN` | Peculiar-velocity constraints and distance information |
| Cosmicflows-4 groups / group velocities | `TRAIN` | Grouped velocity constraints and reduced small-scale virial noise |
| 2MRS | `TRAIN` | Near-infrared large-scale-structure information outside and around the ZoA |
| HIZOA | `TRAIN_CLEAN` | H I information through the ZoA after overlap/decontamination checks |
| Vela-SMGPS | `HOLDOUT` | Primary out-of-sample H I validation catalogue |
| Vela-H I | `HOLDOUT` | Secondary Vela validation catalogue |
| Official CF4 / CF4++ reconstructed grids | `COMPARISON_ONLY` | Numerical benchmark and external comparison unless explicitly cleared for a specific experiment |
| GA-SMGPS | `FUTURE_VALIDATION` | Great Attractor follow-up / independent validation |
| WALLABY products | `COMPARISON_ONLY` / future validation | Wider southern-sky H I comparison and later tests |

**Raw scientific files should remain immutable.** Derived products are expected to carry provenance, version information, file hashes, units, reference frames, quality flags, and transformation history.

Third-party survey data are not assumed to be redistributable by this repository. The project should prefer download/registration scripts and provenance manifests over silently copying external catalogues into version control.

---

## Holdout-first methodology

The first paper depends on protecting the validation set from direct and indirect leakage.

A catalogue marked `HOLDOUT` must not be used for:

- reconstruction;
- parameter tuning;
- smoothing-scale selection;
- threshold selection;
- feature engineering;
- manual previewing used to guide model decisions;
- cached or derived training products;
- hidden crossmatches through alternate catalogue identifiers.

Before a holdout experiment is accepted, Z-ZOA should audit:

1. exact object IDs and aliases;
2. positional crossmatches;
3. redshift / velocity matches;
4. known HIZOA <-> Vela overlaps;
5. duplicate observations and alternate survey names;
6. lineage of every derived training product;
7. caches, notebooks, temporary files, and previous outputs;
8. training-code access to holdout paths;
9. post-hoc tuning after reveal;
10. the frozen run manifest and configuration.

The goal is not merely to place files in different folders. The goal is to make the scientific boundary **auditable**.

---

## Core validation experiment

The central confirmatory experiment is:

```text
RECONSTRUCT WITHOUT MEERKAT
        ->
FREEZE THE PREDICTION
        ->
REVEAL THE WITHHELD H I CATALOGUE
        ->
MEASURE RECOVERY
```

Candidate metrics include:

- mean reconstructed overdensity at withheld H I galaxy positions;
- fraction of withheld galaxies in high-probability overdensity voxels;
- spatial cross-correlation against footprint-matched random catalogues;
- recovery of predefined walls / filaments in `(l, b, cz)`;
- calibration of predicted overdensity probability versus observed H I occupancy;
- topology / web-classification agreement where justified.

Visual similarity alone is not a result. The holdout must be scored against a survey-aware null model.

---

## Hybrid reconstruction

Only after the holdout result is finalized are the withheld H I observations added back into the reconstruction.

The before/after quantities of interest include:

```text
Delta density(x)      = density_hybrid(x) - density_pred(x)
Delta velocity(x)     = velocity_hybrid(x) - velocity_pred(x)
Delta uncertainty(x)  = sigma_pred(x) - sigma_hybrid(x)
```

This allows the project to ask not only **where hidden structure exists**, but also:

> **How much information did the deep H I observations actually add?**

---

## Reconstruction ladder

Z-ZOA is intentionally staged. The project should earn complexity rather than starting with the most expensive inference method.

```text
1. Catalogue registry + provenance
2. Coordinate / unit / reference-frame validation
3. Simple smoothed 3D density baseline
4. Mock-universe and null tests
5. Selection functions / survey masks
6. Wiener filtering / constrained realizations
7. Vela out-of-sample holdout experiment
8. Hybrid reconstruction
9. Robustness sweeps
10. MAP Bayesian reconstruction if justified
11. Posterior sampling at increasing grid resolution if justified
```

A full high-dimensional HMC reconstruction is a possible later phase, not a prerequisite for the first scientifically useful experiment.

---

## Calculation Room

The Calculation Room is the numerical core of the project.

It should remain visually simple and scientifically explicit. A run should expose:

```text
INPUT
  -> transformation
  -> equation / method
  -> output
  -> uncertainty
  -> provenance
```

Important design rules:

- use explicit physical units;
- make cosmological parameters explicit;
- never silently mix heliocentric, Local Group, and CMB reference frames;
- never silently replace missing values;
- never seed production data with fake galaxies;
- preserve source catalogue versions and checksums;
- keep scientific code independent from the frontend;
- produce machine-readable outputs for every important result.

A reproducible run should eventually contain something like:

```text
runs/<RUN_ID>/
  manifest.json
  config.yaml
  checksums.sha256
  results.json
  results.parquet
  methods.md
  warnings.log
  ledger/
  tables/
  exports/
```

---

## 3D Lab Companion

The 3D Lab is a **supplementary research explorer**, not the statistical argument.

Planned layers may include:

- H I galaxy point clouds;
- peculiar-velocity vectors;
- reconstructed density fields;
- uncertainty fields;
- the Galactic obscuration plane;
- cosmic-web classifications;
- streamlines / basin context;
- before-versus-after hybrid comparison.

The viewer should consume frozen numerical outputs produced by the Calculation Room rather than generating scientific claims interactively.

---

## XRPL Testnet run anchoring

Z-ZOA plans to use **XRPL Testnet** as a lightweight development-time chronology / integrity receipt for important research stages.

The idea is intentionally simple:

```text
frozen scientific run
      -> SHA-256
      -> XRPL Testnet transaction memo
      -> transaction hash + ledger receipt
      -> later verification
```

Planned anchor stages include:

```text
TRAIN_START
PREDICTION_FROZEN
HOLDOUT_REVEAL
VALIDATION_COMPLETE
HYBRID_COMPLETE
PAPER_CANDIDATE
```

The most important anchor is `PREDICTION_FROZEN`, which should occur before holdout access is enabled for an anchor-required experiment.

XRPL does **not** prove the science is correct. It can only help demonstrate that a particular cryptographic fingerprint of a frozen run was committed before later stages.

Testnet is a development network and may be reset. It is **not** a substitute for conventional publication preservation such as source-control releases, archived reproducibility bundles, or research repositories.

No private data, catalogue rows, unpublished arrays, API keys, or signing secrets should ever be written to the ledger.

---

## Reproducibility target

A strong Z-ZOA result should be reproducible from a clean environment using documented public inputs and frozen configuration.

The eventual publication bundle should aim to provide:

- source code;
- dependency/environment lock information;
- dataset registry and provenance;
- exact catalogue cuts and masks;
- configuration files;
- random seeds;
- training / holdout role declarations;
- reconstruction outputs needed for the central figures;
- null-test outputs;
- paper tables;
- machine-readable predictions;
- checksums;
- step-by-step reproduction instructions.

The strongest standard is a clean-room rebuild in which the frozen prediction can be regenerated using only approved training inputs, without the holdout dataset being mounted or readable.

---

## Planned paper outputs

The first paper should be driven by verified numerical outputs, not by the interactive viewer.

A minimal paper-quality result set would include:

1. survey footprints and training / holdout definition;
2. reconstruction without the selected MeerKAT holdout;
3. uncertainty / probability field;
4. frozen prediction regions;
5. withheld MeerKAT galaxies revealed over the prediction;
6. null-distribution / significance result;
7. hybrid before-versus-after reconstruction;
8. robustness and sensitivity tests;
9. reproducibility and leakage-audit report.

The manuscript should avoid claims such as:

- "first map of the Zone of Avoidance";
- "first prediction of hidden ZoA structure";
- "blind discovery of Vela";
- exact reproduction of another collaboration's reconstruction unless every input and preprocessing step has actually been reproduced.

---

## Project status

**Status: early-stage independent research software / methodology development.**

Current focus:

- establish the reproducible calculation foundation;
- register and audit public datasets;
- enforce holdout boundaries;
- validate coordinate, unit, cosmology, and velocity handling;
- build mock-universe tests before trusting real reconstructions;
- progress toward the first Vela holdout experiment.

The scientific design is expected to evolve as the implementation, data audits, and validation tests expose new constraints.

---

## Repository philosophy

Z-ZOA should prefer:

```text
public data
+ explicit assumptions
+ documented transformations
+ uncertainty
+ leakage controls
+ null tests
+ reproducible code
+ falsifiable predictions
```

over impressive-looking visualizations without a controlled scientific test.

---

## Independent research disclaimer

Z-ZOA is an **independent research project**. It is not an official project of, endorsed by, or affiliated with the Cosmicflows, MeerKAT, SARAO, WALLABY, ASKAP, HIZOA, 2MRS, or other survey collaborations referenced by the research plan.

Names of surveys, catalogues, instruments, and collaborations are used only to identify public scientific data products and prior work.

---

## License

Software in this repository is released under the [MIT License](LICENSE).

Scientific datasets obtained from external archives remain subject to their original licences, acknowledgements, citation requirements, and data-use policies.

---

## Author

**Zhane Grey**  
Independent research project, 2026

---

> *Same sky. Better constraints. A clearer reconstruction.*
