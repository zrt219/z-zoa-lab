# Z-ZOA Formal Preregistered Analysis Plan (Prompt 15)

**Project Title**: *Z-ZOA: Out-of-Sample Reconstruction and H I Validation of Large-Scale Structure Across the Galactic Zone of Avoidance*  
**Date of Preregistration**: September 15, 2026 (Pre-Reveal)  
**Contract Hash (SHA-256)**: Sealed in `docs/preregistered_analysis_plan.json`  

---

## 1. Primary Hypothesis
The continuous 3D cosmological matter distribution reconstructed from peculiar velocity and redshift surveys outside the MeerKAT Vela-SMGPS footprint anticipates a statistically significant excess density contrast at the locations of the withheld Vela-SMGPS galaxies:
$$\mathbb{E}[\delta(\mathbf{x}_{\text{holdout}})] > \mathbb{E}[\delta(\mathbf{x}_{\text{null}})]$$

## 2. Locked Hyperparameters (Pre-Reveal)
- **Gaussian Smoothing Length**: $R_s = 10.0\,h^{-1}\text{ Mpc}$
- **Cartesian Grid Size**: $N_{\text{grid}} = 32^3$ across a $400\,h^{-1}\text{ Mpc}$ box ($\Delta x = 12.5\,h^{-1}\text{ Mpc}$)
- **Cosmological Parameters**: $H_0 = 74.6\text{ km s}^{-1}\text{ Mpc}^{-1}$, $\Omega_m = 0.30$, $\Omega_\Lambda = 0.70$
- **Velocity Cut**: $cz_{\max} = 25,000\text{ km s}^{-1}$
- **Ensemble Realizations**: $N = 20$ constrained realizations (base seed 1000)

## 3. Survey-Matched Null Model
Null distribution is sampled by drawing 1,000 realizations of 39 synthetic coordinates strictly within:
$$260^\circ \le \ell \le 290^\circ, \quad -2^\circ \le b \le +1^\circ, \quad 0 \le cz \le 25,000\text{ km s}^{-1}$$
modulated by the survey detection weight $W(cz) = (cz_{\max} - cz) / (cz_{\max} - cz_{\min})$.

## 4. Confirmatory vs. Exploratory Demarcation
Any metric, cut, or parameter variation evaluated subsequent to holdout unsealing must be classified as **EXPLORATORY** and cannot be substituted into primary confirmatory tables.
