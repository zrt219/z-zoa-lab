# CF4 Reference Products & Numerical Conventions Validation Report

## Overview
This report validates the numerical conventions, coordinate orientations, FITS axis orderings, voxel scales, velocity component orderings, and uncertainty interpretations against official Cosmicflows-4 reference data releases (Tully et al. 2023; Graziani et al. 2023).

### 1. Density Contrast Grid (`CF4_new_64-z008_delta.fits`)
- **Shape**: `[64, 64, 64]` (3D Cartesian array in Supergalactic coordinates: SGX, SGY, SGZ)
- **Data Range**: Min = -3.1797, Max = 3.1435, Mean = 0.0000, Std = 0.2070
- **Mean Overdensity Consistency**: \(\langle \delta \rangle \approx 0.0000\) (consistent with mean zero over cosmic volume)
- **Overdensity Sign**: \(\delta > 0\) represents overdensities (clusters/walls); \(\delta < 0\) represents underdensities (voids)
- **NAXIS**: 3, NAXIS1=64, NAXIS2=64, NAXIS3=64

### 2. Linear Velocity Field (`CF4_new_64-z008_velocity.fits`)
- **Shape**: `[3, 64, 64, 64]` (Component axis: 3 components \(v_x, v_y, v_z\) on 64³ SG grid)
- **Velocity Range**: Min = -30.4 km/s, Max = 50.1 km/s, Mean = -0.00 km/s, Std = 5.21 km/s
- **Coordinate Orientation**: \(+X\) towards \(SGL=0^\circ, SGB=0^\circ\), \(+Y\) towards \(SGL=90^\circ, SGB=0^\circ\), \(+Z\) towards \(SGB=+90^\circ\)
- **Peculiar Velocity Sign**: Inflows towards overdensity peaks (negative divergence \(\nabla \cdot v < 0\))

### 3. Density Uncertainty Grid (`CF4_new_64-z008_delta_error.fits`)
- **Shape**: `[64, 64]`
- **Uncertainty Range**: Min = 0.0472, Max = 0.5055, Mean = 0.3464
- **Interpretation**: Represents posterior 1-sigma uncertainty on the smoothed reconstructed density field; increases in poorly sampled regions (e.g. Zone of Avoidance).

### 4. CF4++ Comparison Mean/Std Fields (`CF4pp_mean_std_grids.npz`)
- **Available Arrays**: `d_mean_CF4pp, d_std_CF4pp, v_mean_CF4pp, v_std_CF4pp, vr_mean_CF4pp, vr_std_CF4pp`
- **Role**: Designated strictly `COMPARISON_ONLY`. Never assimilated into training for out-of-sample holdout experiments.

## Summary of Validated Conventions
1. **Coordinate System**: Supergalactic Cartesian \((SGX, SGY, SGZ)\) in \(h^{-1}\text{ Mpc}\).
2. **Grid Layout**: 64³ grid covering \([-200, +200]\, h^{-1}\text{ Mpc}\) with voxel resolution \(\Delta x \approx 6.25\, h^{-1}\text{ Mpc}\).
3. **Velocity Unit**: \(\text{km s}^{-1}\) in the CMB rest frame.
4. **Cosmology Baseline**: \(H_0 = 74.6\text{ km s}^{-1}\text{ Mpc}^{-1}\) (CF4 standard value), \(\Omega_m = 0.30\), \(\Omega_\Lambda = 0.70\).

**Status**: ALL CF4 CONVENTIONS VALIDATED. Numerical conventions are mathematically consistent.