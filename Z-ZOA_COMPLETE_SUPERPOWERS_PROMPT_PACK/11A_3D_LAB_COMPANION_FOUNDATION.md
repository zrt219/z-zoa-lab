# /goal — Build the Z-ZOA 3D Lab Companion foundation

Build the 3D Lab as a **read-only scientific companion** to the Calculation Room. It visualizes authorized artifacts; it does not generate or modify the paper result.

Use `visual_refs/03_3d_lab_companion.png` as design inspiration only. Do not copy illustrative fake numbers/galaxies into production.

## Core separation

```text
Calculation Room
  produces frozen scientific artifacts
        |
        v
read-only data contract
        |
        v
3D Lab Companion
  explores those artifacts
```

The 3D Lab must never write scientific config, alter reconstruction parameters, change masks, tune thresholds, or unlock HOLDOUT data.

## Route / shell

Add an explicit 3D Lab route or workspace within the same project, following the current frontend architecture.

The UI should provide:
- run selector restricted to authorized run artifacts;
- layer panel;
- camera controls;
- slice controls where supported;
- selected-object/voxel inspector;
- run metadata/provenance banner;
- warning when viewing synthetic/mock data;
- warning when a run is not frozen/validated.

## Rendering technology

Prefer Three.js/WebGL through the existing frontend stack if already used. Keep the rendering layer isolated from scientific calculations.

Do not make the scientific Python core depend on Three.js.

## Performance

The viewer must support bounded, chunked/decimated representations rather than loading giant raw catalogues or full volumes into the browser blindly.

Design for:
- typed-array/binary payloads when justified;
- server-side spatial/LOD filtering;
- volume downsampling or chunking;
- deterministic visualization transforms;
- visible indication when a layer is decimated/downsampled.

## Scientific integrity

Every visible layer must be traceable to:
- run ID;
- artifact ID/path;
- dataset parents;
- units;
- coordinate convention;
- transformation version;
- visualization-only transforms.

A screenshot is never the canonical result.

## Tests

Test:
- only approved run artifacts are selectable;
- mock runs are clearly labeled;
- an empty run renders an honest empty state;
- malformed layer metadata fails safely;
- coordinate axes/orientation match the data contract;
- viewer cannot mutate run config through any API call.

## Completion gate

Render one synthetic frozen run through the real artifact contract with axes, run metadata, and at least one simple point/field layer. No real HOLDOUT data yet.
