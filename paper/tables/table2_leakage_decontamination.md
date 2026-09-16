| Stage | Criteria | Objects | Action |
| --- | --- | --- | --- |
| Raw HIZOA-S Detections | Initial Survey Ingestion | 883 | Ingested into raw catalog |
| Coordinate Normalization | ICRS -> Galactic & Supergalactic | 883 | Standardized to km/s & Mpc |
| Vela Footprint Cross-Match | 260<=l<=290 deg, -2<=b<=1 deg | 39 | Quarantined in exclusion list |
| TRAIN_CLEAN Assembly | 883 raw - 39 quarantined | 844 | Sealed for training without leakage |
| Double-Blind Reveal Gate | Cryptographic freeze token match | 39 | Unblinded only after freeze seal |
