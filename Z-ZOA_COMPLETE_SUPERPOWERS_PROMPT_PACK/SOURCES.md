# Sources and scientific guardrails

These prompts were written to keep the Z-ZOA workflow aligned with public survey documentation and reproducibility practice.

## Primary sources

1. Extragalactic Distance Database (EDD) — Cosmicflows-4 catalogues. The public CF4 products include 55,877 individual galaxy distances, 38,057 grouped entries, and the group-velocity catalogue.  
   https://edd.ifa.hawaii.edu/

2. Vela-SMGPS H I catalogue — 843 detections. The paper reports that the survey footprint contains 39 previously known HIZOA detections and that Vela-SMGPS recovered all of them. Those overlaps are a concrete leakage risk for a HIZOA-trained / Vela-held-out experiment.  
   https://academic.oup.com/mnras/article/531/3/3486/7682409

3. WALLABY Pilot Survey DR2 — public source catalogue and value-added products. The standard 30 arcsec Phase-2 source catalogue contains 1,760 detections and is accessible via CADC/CASDA/TAP.  
   https://wallaby-survey.org/data/data-pilot-survey-dr2/

4. Data leakage and reproducibility in scientific modelling — leakage can create severely optimistic validation results, so all training/validation boundaries must be explicit, machine-enforced, and reported.  
   https://pmc.ncbi.nlm.nih.gov/articles/PMC10499856/

## Z-ZOA-specific rules

- Vela-SMGPS and Vela-HI are HOLDOUT datasets for the first Vela experiment.
- HIZOA may be used only after decontamination against the selected holdout.
- CF4++ / hybrid-ZoA products that assimilate MeerKAT are COMPARISON_ONLY for the holdout experiment.
- The leakage audit is allowed to compare TRAIN and HOLDOUT metadata/rows only to create exclusion lists and a leakage report. It must not tune reconstruction parameters or expose holdout-driven science results to the training phase.
- After the leakage audit, reconstruction code should operate on a physically/logically isolated TRAIN_CLEAN snapshot with no HOLDOUT mount or read permission.
