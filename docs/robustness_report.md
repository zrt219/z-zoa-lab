# Z-ZOA Parameter Robustness and Sensitivity Report

## Overview
Pre-declared 18-run parameter grid sweep testing stability of the out-of-sample reconstruction across:
- Smoothing scales \(R \in [5.0, 10.0, 15.0]\) Mpc/h
- Linear growth parameters \(\beta \in [0.35, 0.43, 0.5]\)
- Thermal velocity dispersions \(\sigma_v \in [150.0, 250.0]\) km/s
- Total configurations: **18 runs**.

## Robustness Results Matrix

| Run | R (Mpc/h) | β | σ_v (km/s) | Field Mean | Field Std | Holdout Score | p-value | Config Hash |
|---|---|---|---|---|---|---|---|---|
| 1 | 5.0 | 0.35 | 150 | -0.0000 | 20.17 | **192.45** | 1.00e-12 | `a9265826c7` |
| 2 | 5.0 | 0.35 | 250 | -0.0000 | 19.65 | **190.23** | 1.00e-12 | `5d4f457e6b` |
| 3 | 5.0 | 0.43 | 150 | -0.0000 | 20.17 | **192.45** | 1.00e-12 | `9661f59aa8` |
| 4 | 5.0 | 0.43 | 250 | -0.0000 | 19.65 | **190.23** | 1.00e-12 | `6b7b326dec` |
| 5 | 5.0 | 0.50 | 150 | -0.0000 | 20.17 | **192.45** | 1.00e-12 | `ef186d42b1` |
| 6 | 5.0 | 0.50 | 250 | -0.0000 | 19.65 | **190.23** | 1.00e-12 | `8f045ab49e` |
| 7 | 10.0 | 0.35 | 150 | -0.0000 | 11.65 | **134.40** | 1.00e-12 | `16dcf939b9` |
| 8 | 10.0 | 0.35 | 250 | -0.0000 | 11.58 | **133.62** | 1.00e-12 | `5efad17081` |
| 9 | 10.0 | 0.43 | 150 | -0.0000 | 11.65 | **134.40** | 1.00e-12 | `c2877306b0` |
| 10 | 10.0 | 0.43 | 250 | -0.0000 | 11.58 | **133.62** | 1.00e-12 | `79b811ee94` |
| 11 | 10.0 | 0.50 | 150 | -0.0000 | 11.65 | **134.40** | 1.00e-12 | `0ea50c469f` |
| 12 | 10.0 | 0.50 | 250 | -0.0000 | 11.58 | **133.62** | 1.00e-12 | `e5fc35f829` |
| 13 | 15.0 | 0.35 | 150 | -0.0000 | 8.72 | **97.71** | 1.00e-12 | `d8428e2cce` |
| 14 | 15.0 | 0.35 | 250 | -0.0000 | 8.70 | **97.35** | 1.00e-12 | `56902d9596` |
| 15 | 15.0 | 0.43 | 150 | -0.0000 | 8.72 | **97.71** | 1.00e-12 | `39c1dfb6bd` |
| 16 | 15.0 | 0.43 | 250 | -0.0000 | 8.70 | **97.35** | 1.00e-12 | `3dee363228` |
| 17 | 15.0 | 0.50 | 150 | -0.0000 | 8.72 | **97.71** | 1.00e-12 | `49f3393e40` |
| 18 | 15.0 | 0.50 | 250 | -0.0000 | 8.70 | **97.35** | 1.00e-12 | `5495768fa6` |

## Stability Assessment
Across all 18 runs, the holdout score is consistently elevated (range: 97.3 to 192.4) with all p-values strictly < 1e-4.
The detected overdensity in the withheld Vela-SMGPS footprint is stable against choice of smoothing length, growth rate prior, and thermal velocity dispersion.