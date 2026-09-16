# /goal — Add the revealed MeerKAT data and quantify information gain

After the frozen holdout score is complete, build the hybrid reconstruction by adding the previously withheld Vela-SMGPS constraints according to the documented hybrid method.

Keep the baseline/frozen run immutable.

## Quantify

For matched voxels compute:

```text
delta_density = density_hybrid - density_pred
delta_velocity = velocity_hybrid - velocity_pred
delta_sigma = sigma_pred - sigma_hybrid
```

Also quantify changes to predefined overdensity peaks and any cosmic-web/topology classification used by the paper.

The key question is not merely whether the map looks different. It is how much the new H I information changes the inferred field and reduces uncertainty.

Produce machine-readable delta fields and tables suitable for paper figures.
