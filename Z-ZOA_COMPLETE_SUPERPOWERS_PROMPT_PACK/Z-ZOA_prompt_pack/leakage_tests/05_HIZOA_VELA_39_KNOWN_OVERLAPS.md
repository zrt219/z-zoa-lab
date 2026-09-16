# Leakage test 05 — HIZOA / Vela-SMGPS known overlap sanity check

The published Vela-SMGPS paper reports that its footprint contains 39 HIZOA detections and that Vela-SMGPS recovered all of them.

Use our actual downloaded catalogue versions to independently cross-match HIZOA and Vela-SMGPS.

## Requirements

- do not hardcode 39 as the computed answer;
- identify the actual overlapping rows;
- compare our result with the published 39-object statement;
- if our count differs, investigate coordinate formats, catalogue cuts, footprint definitions, duplicate handling, and catalogue release differences;
- write an explicit discrepancy explanation before proceeding;
- add confirmed overlapping HIZOA rows to the training exclusion list.

Output `leakage/05_hizoa_vela_overlap.parquet` and `05_hizoa_vela_overlap_report.md`.
