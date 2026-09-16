# /goal — Make the analysis produce paper-ready tables and figures automatically

Build a publication-output command that consumes frozen/validated run artifacts and generates the manuscript's central outputs without manual spreadsheet editing.

## Required outputs

At minimum:
1. data/footprint summary table;
2. leakage/decontamination summary table;
3. reconstruction/method configuration table;
4. holdout validation metrics table;
5. hybrid information-gain table;
6. robustness table;
7. publication figures for reconstruction, uncertainty, holdout scoring/null distribution, and before-vs-after hybrid changes.

Figures may be 2D scientific plots. The Calculation Room UI itself remains non-visual/minimal.

Export PDF/SVG/PNG as appropriate plus underlying CSV/Parquet data and figure-generation scripts. Record source run IDs in figure metadata/captions.
