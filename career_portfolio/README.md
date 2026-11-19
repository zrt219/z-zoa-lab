# Z-ZOA | Astronomy software portfolio entry point

This small **read-only catalog QA utility** complements the existing research system in \`z-zoa-lab\`. It does not replace \`research/\`, rerun the published experiment, or access quarantined observational data.

Run from the repository root:

\`\`\`bash
python -m career_portfolio.catalog_qc --csv path/to/authorized_training_catalog.csv --out local_catalog_report.json
python -m unittest discover -s career_portfolio -p 'test_*.py'
\`\`\`

The input CSV must contain \`object_id,l_deg,b_deg,cz_km_s\`. It checks coordinate bounds and duplicate IDs, records SHA-256 data provenance, and counts sources inside the simple optical Zone of Avoidance sky mask (\`|b| < 10 deg\`).

This is descriptive training-catalog quality control, **not** a new astronomical detection, a Bayesian reconstruction, or confirmation of the research result. This utility rejects paths with a \`HOLDOUT\` directory component and does not open the MeerKAT validation catalog.

Future work should integrate a properly documented selection function and blind recovery scoring through the existing repository \`DataGateway\`, freeze/reveal, and leakage-audit workflow. All root \`AGENTS.md\` invariants remain authoritative.
