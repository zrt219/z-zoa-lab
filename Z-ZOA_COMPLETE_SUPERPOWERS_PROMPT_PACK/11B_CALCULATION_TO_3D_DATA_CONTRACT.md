# /goal — Define the Calculation Room -> 3D Lab scientific artifact contract

Create a versioned, validated data contract between numerical research outputs and the 3D viewer.

The goal is to make the viewer replaceable without changing the science.

## Contract principles

- 3D Lab consumes exported artifacts, not Python objects in memory.
- Contract is versioned.
- Units and coordinate frames are mandatory.
- Artifact lineage is mandatory.
- Viewer-specific styling is not stored in scientific arrays.
- HOLDOUT authorization is evaluated before artifact delivery.

## Minimum artifact types

Define typed schemas for:

```text
PointCatalogLayer
VectorFieldLayer
ScalarVolumeLayer
StreamlineLayer
MaskPlaneLayer
StructureLabelLayer
RunComparisonLayer
```

Adapt names to project conventions.

### Point catalog metadata

Include:
- positions and coordinate frame;
- optional object IDs safe for current stage;
- source dataset/run;
- units;
- allowed display fields;
- decimation/selection metadata.

### Scalar volume

Include:
- grid origin;
- spacing;
- dimensions;
- axis order;
- coordinate frame;
- scalar quantity name;
- units/dimensionless status;
- mean/uncertainty/probability semantics;
- missing/out-of-domain policy.

### Vector field

Include:
- component order;
- velocity units/frame;
- grid definition;
- interpolation notes;
- uncertainty linkage if available.

## Exporter

Build a Calculation Room exporter that converts an approved run into a 3D-lab bundle such as:

```text
runs/<RUN>/exports/3d/v1/
  manifest.json
  layers.json
  points.*
  volumes/*
  vectors/*
  streamlines/*
  checksums.sha256
```

Use efficient formats justified by the stack. Do not require CSV for large arrays if a better format already exists.

## Viewer API

Expose read-only endpoints for:
- list authorized run bundles;
- get bundle manifest;
- get layer metadata;
- fetch bounded/chunked data.

The API must refuse unauthorized role/stage combinations.

## Tests

Round-trip a synthetic known cube/point set from Python export -> backend -> frontend loader and verify positions, axis orientation, scalar values, units, and hashes.

## Completion gate

A synthetic layer bundle created only by the scientific exporter must render identically after a clean frontend reload. No manual frontend data massaging is allowed.
