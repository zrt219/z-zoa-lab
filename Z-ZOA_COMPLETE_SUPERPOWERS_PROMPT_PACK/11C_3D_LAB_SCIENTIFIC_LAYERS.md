# /goal — Implement the scientific layers in the 3D Lab

Using only the versioned 3D artifact contract, implement the core Z-ZOA layers.

## Layer 1 — H I / galaxy point catalogue

Render authorized point catalogues with:
- stable coordinate transform;
- selectable objects;
- basic metadata inspector;
- point-size/opacity controls that affect only display;
- optional coloring by an explicitly named field such as cz/redshift/survey.

Do not encode scientific meaning into arbitrary colors without a legend.

## Layer 2 — Density field

Render a reconstructed scalar density/overdensity volume or slices. Clearly display:
- run ID;
- quantity name;
- smoothing/grid scale;
- coordinate frame;
- whether this is mean/MAP/single realization.

## Layer 3 — Uncertainty/probability

Support uncertainty or probability as a separate selectable layer. Never make uncertainty disappear merely because the mean field is being shown.

## Layer 4 — Velocity field

Render vectors/cones or a scientifically defensible reduced representation. Preserve units and direction convention. Make decimation obvious.

## Layer 5 — Streamlines

If streamlines are supplied by the scientific backend, render them. Do not integrate a scientifically new velocity solution in the browser.

## Layer 6 — Milky Way / ZoA mask context

Render the Galactic plane/ZoA observational mask as context. Label it as a survey/analysis mask, not a physical wall in space.

## Layer 7 — Structure annotations

Allow labels for known/derived structures only from an artifact or curated metadata file with provenance. Do not hardcode unverified claims into the scene.

## Inspector

Selecting a voxel/object should show:
- coordinates;
- relevant scalar/vector values;
- uncertainty if available;
- source run/layer;
- parent dataset(s);
- display transform/LOD status.

## Tests

Use synthetic geometries where truth is known to test:
- axis orientation;
- position mapping;
- vector sign/direction;
- volume indexing;
- selection accuracy;
- mask placement;
- LOD/decimation disclosure.

## Completion gate

All seven layer types can coexist for a synthetic run without the browser becoming the source of any new scientific quantity.
