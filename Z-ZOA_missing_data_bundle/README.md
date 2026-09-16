# Z-ZOA Missing Data Acquisition Bundle

This bundle fills the two dataset gaps visible in the supplied project screenshot:

1. **GA-SMGPS Great Attractor catalogue** — 477 H I detections. Intended role: `HOLDOUT` / future validation.
2. **WALLABY Pilot DR2 30-arcsec source catalogue** — official public DR2 source table. Intended initial role: `COMPARISON_ONLY` (promote to `VALIDATION` only after leakage rules are defined).

The screenshot already showed CF4 individual/group/group-velocity catalogues, 2MRS tables 3/6, HIZOA, Vela-HI, Vela-SMGPS, CF4 grids, and CF4++ grids, so this bundle does not duplicate them.

## Why this bundle contains a downloader rather than copied catalogue bytes

The archive endpoints used by VizieR/CADC are query services. The ChatGPT file runtime used to build this ZIP cannot directly execute those external archive queries, so this bundle contains a reproducible one-command downloader that pulls the official tables directly from their authoritative services onto your computer and immediately records SHA-256 checksums and source metadata.

## Quick start on Windows

Extract this ZIP into your Z-ZOA project root, open PowerShell there, then run:

```powershell
powershell -ExecutionPolicy Bypass -File .\download_missing.ps1
```

Or manually:

```powershell
py -m pip install -r requirements.txt
py .\download_missing.py --repo-root .
```

## Files created

```text
datasets/
├── HOLDOUT/
│   └── GA_SMGPS/
│       ├── ga_smgps_477.csv
│       └── ga_smgps_source.json
└── reference/
    └── WALLABY_DR2/
        ├── wallaby_dr2_source_catalogue.csv
        └── wallaby_dr2_source.json

datasets/manifests/missing_download_manifest.json
```

## Authoritative sources

### GA-SMGPS
- VizieR catalogue: `J/MNRAS/529/L88/ga-smgps`
- Paper DOI: `10.1093/mnrasl/slad196`
- Expected catalogue size: **477 rows**
- VizieR page: https://vizier.cds.unistra.fr/viz-bin/VizieR?-source=J/MNRAS/529/L88

### WALLABY Pilot DR2
- CADC/CANFAR TAP service: https://ws-uv.canfar.net/youcat
- Table: `cirada.Wallaby_dr2_source_catalogue`
- Data DOI: `10.25919/qw7w-tn96`
- Release paper: Murugeshan et al. 2024, PASA 41, e088; arXiv:2409.13130
- Release page: https://wallaby-survey.org/data/data-pilot-survey-dr2/

## Holdout warning

`GA_SMGPS` is written under `datasets/HOLDOUT/`. Do not let training/reconstruction code inspect or tune against it before a frozen validation stage. WALLABY DR2 is initially written under `reference/` because it should remain comparison-only until a clean train/validation boundary is defined.
