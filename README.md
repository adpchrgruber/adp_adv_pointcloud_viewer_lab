# Scan Matter — a Point-Cloud Workbench

**[Open the live workbench →](https://adpchrgruber.github.io/adp_adv_pointcloud_viewer_lab/)**

![A courtyard scan, a vessel drawn in brush-stroke points, and vessels cut into colour fragments](docs/preview.png)

Open laser scans and photogrammetry clouds in the browser, assemble several of them in
one space, measure and clip them, and cut them into **colour families** — fragments you
can move and recombine. Everything runs locally: files are read on your computer and
never uploaded.

It combines the simplicity of [LidarView](http://lidarview.com/) (one page, drop a file,
it shows) with the strengths of [Potree](https://potree.org) (octree level of detail,
point budget, adaptive point size, eye-dome lighting, measuring and clipping).

## Use

1. **01 Load & assemble** — drop **LAS, LAZ, PLY, XYZ / TXT / CSV / PTS** files anywhere,
   use *Load scans…*, paste a URL, or open the page with `?url=https://…/scan.laz`.
   Each scan gets an octree on load (in a background worker). Click a scan in the list
   or in the view to select it, then **G** move · **R** rotate · **X** scale.
   *Up* swaps Z-up (survey, LAS) and Y-up (many PLY / photogrammetry exports),
   *Ground* sets it on the ground plane, *Copy* duplicates it.
   Georeferenced scans of the same area keep their real relative positions; anything
   else is placed next to what is already there.
2. **02 View** — colour by **RGB, Height, Intensity, Class** (ASPRS codes), **Family**,
   **Depth**, **Density** (local point density) or **Level** (octree level). *Size* with *Adaptive* sizing (follows the octree level, so the cloud stays
   closed at every distance) or *Fixed px*. *Budget* is the most points drawn at once.
   *EDL* shades points by the depth of their neighbours and outlines silhouettes.
   Views Top / Front / Side / Iso, turntable (Space), **W A S D Q E** to fly; *Frame* and
   *Clear* sit top right.
   **Point shape**: square, circle, triangle, oval, sphere (lit from the upper left),
   cube (isometric, three shaded faces), spike (four-pointed star), ring — and two
   generative ones: **shard** (each point a randomly turned, irregular splinter) and
   **brush** (tapered strokes that follow a smooth flow field across the scene).
   **Density** varies the shapes by the local point density: to the right sparse
   regions, to the left dense regions get larger, more varied, turned shapes.
3. **03 Measure, select & clip** — **Point** (I) reads a point's source coordinates
   (real-world values for georeferenced files), colour, class and family. **Dist.** (M)
   and **Height** (H) measure between two points. **Wand** selects by colour: it floods
   from a clicked point through neighbouring points whose colour stays within
   *Tolerance* (ΔE in CIELAB); Shift-click adds; *Cut selection* makes the patch and the
   rest two scans. The **clip box** keeps or cuts what is inside; *Clip → scan* turns
   the result into a new scan.
4. **04 Colour families** — clusters the colours of every visible scan together
   (k-means in CIELAB, 2–16 families). Click a swatch to hide a family, Shift-click to
   isolate it. **Split into scans** makes every visible family of every visible scan a
   fragment of its own — select one and move it.
5. **05 Depth** — segmentation by distance from the camera, the depth-of-field idea with
   real depth. *Set focus* and click a point (or *Focus centre*); *Field* is the depth
   of the sharp zone. **3 zones** splits into foreground · in focus · background,
   **Layers** into equal depth bands front to back. *Preview* colours them live — the
   split follows the camera — and *Cut by depth* freezes the current view: every zone or
   layer becomes a scan to pull apart like a stage flat. **Blur** adds a depth-of-field
   look: points outside the sharp zone blur by their distance from it.
6. **06 Texture** — maps a 2D texture onto the points. Eight tileable noise samples are
   generated in the page — *clouds, marble, wood, cells, craquelure, ridged, turbulence,
   terrazzo* — or load *Own image…*. Points have no surface to wrap an image around, so
   the texture is **projected**: from the *Top*, *Front* or *Side*, or wrapped around a
   *Cylinder* or *Sphere* through the scene centre. *Replace*, *Multiply* or *Overlay*
   it with the colours; *Tile* sets the size of one tile (in % of the scene). **Bake**
   writes the result into the colours (so it exports and clusters), **Cut** splits every
   visible scan into the light and dark parts of the texture — noise becomes fragments —
   and *Restore* brings the original colours back.
7. **07 Line drawing** — after Fritz Panzer's wire sculptures, everyday objects redrawn
   1:1 as lines in space. **Draw outlines** traces where colour families meet (every
   cube of *Detail* × the point spacing takes its majority family, smoothed once more,
   so only coherent patches give borders) and where the cloud itself ends — rims, wall
   tops, ends (the points around a cube lie to one side of it, measured along the
   surface). *Tidy* drops lines shorter than that many nodes. **Contours** and a
   **Section** (X, Z or Plan, with *Position* and *Flip side*) can be previewed live on
   the points and drawn as lines. **Points on/off** (P) leaves the wire drawing alone in
   space; *Width*, *Ink / Blue / Colours* and *See-through* style the wire; **Export
   lines DXF** writes every line as a 3D LINE on the layers OUTLINES, CONTOURS and
   SECTION (Z up, real-world coordinates) for Rhino, AutoCAD or a wire-bending plan.
8. **08 How point clouds work** — a short course in seven lessons, each with a *Show*
   that demonstrates it on the loaded scan (and *Hide* that puts the view back):
   points, not surfaces · every point is a record · sampling is uneven (colour by
   density) · level of detail (octree boxes, colour by level) · neighbourhoods (click a
   point) · coordinates and 32-bit precision · shading without surfaces (EDL off).

**Output** — *Export PLY* writes every visible point — assembled, clipped, with hidden
families left out — as binary PLY (double x y z, Z up, georeferenced, plus RGB,
intensity, classification and family): opens in CloudCompare, Rhino, Blender,
MeshLab. *Screenshot* saves a PNG, *Record turn* one turntable revolution as video.

### Presets

| Preset | |
|---|---|
| Courtyard | 2.6 M points — stone floor with moss, brick walls with plaster, rust and a blue door, a colonnade, a tree |
| Vessels | 1.2 M points — celadon jar, raku bowl, porcelain bottle on a plinth: made for colour families |
| Terrain | 6 M points — 600 m valley with forest, rock, snow and water, classified, georeferenced: a level-of-detail test |

### Example files (`examples/`)

| File | |
|---|---|
| `arch.las` | brick portal, LAS 1.2 point format 2, georeferenced |
| `bowl.ply` | raku bowl, binary PLY with RGB |
| `boulder.xyz` | boulder with lichen, ASCII `x y z r g b` |

Generated by `tools/make_examples.py` (Python 3, standard library only).

## How it works

- **Reading** happens in a Web Worker: LAS 1.0–1.4 (point formats 0–10), LAZ through
  [laz-perf](https://github.com/hobuinc/laz-perf) (fetched from the CDN only when a .laz
  file is opened), PLY (ASCII and binary), and delimited text with column detection.
  Clouds over 40 M points are decimated on read.
- **Octree** (after Potree's converter): each node keeps one point per cell of a 128³
  grid, taken in random order so it is an even subsample; the rest fall to its eight
  children. Points are stored node by node, so each node is one slice of the arrays.
- **Level of detail** (after Potree): every frame the nodes are opened in order of their
  size on screen until the point budget is spent; nodes outside the view are skipped.
- **Adaptive point size** (after Potree): the drawn nodes are encoded in a small texture
  (child mask and offset per node); the vertex shader walks it to the deepest drawn node
  around each point and sizes the point by that level's spacing.
- **Eye-dome lighting** (Boucheny 2009, as in Potree and CloudCompare): points render
  into a target with a depth texture; a full-screen pass darkens each pixel by how much
  nearer its neighbours are, in log depth. The same pass does the depth-of-field blur
  (a gathered circle of confusion per pixel).
- **Neighbourhoods** (wand, density) use a hashed voxel grid in the worker;
  point spacing and density are measured once when a scan is built.

## Credits

Ideas are borrowed, the code is written fresh for this page.

- **[Potree](https://github.com/potree/potree)** — Markus Schütz, TU Wien (BSD-2-Clause):
  octree sampling, screen-size-ordered traversal with a point budget, visible-node
  texture for adaptive point size, EDL pass, clip box and measuring tools.
- **[LidarView](http://lidarview.com/)** — xtsense: one-page local viewer, decimation to a
  point buffer, colour modes, WASD fly keys, the *Animate* turntable, `?url=` loading.
- **Eye-dome lighting** — Christian Boucheny, *Visualisation scientifique de grands
  volumes de données*, 2009.
- **[laz-perf](https://github.com/hobuinc/laz-perf)** — Hobu Inc. (Apache-2.0), used as is
  for LAZ decompression.
- **[three.js](https://threejs.org)** (MIT).
- **Fritz Panzer** — artistic reference for the line drawing: his wire sculptures, objects
  and rooms drawn 1:1 in space.

## Run locally

Single self-contained `index.html`, no build step; three.js from the CDN. Example
files need http:

```bash
python3 -m http.server
```

## Repository layout

```
index.html        the whole app (HTML, CSS, worker and JS module)
examples/         example scans (LAS, PLY, XYZ)
tools/            generator for the examples
docs/preview.png  social / README preview image
```

## Scripting

The page exposes `window.points` in the browser console:

```js
points.loadPreset('terrain')
points.loadURL('examples/arch.las')
points.params.k = 8; points.runFamilies()
points.splitFamilies()
points.setDepthMode('layers'); points.cutByDepth()
points.useTexture('marble'); points.setTexMode(3); points.bakeTexture()
points.drawOutlines(); points.setPointsVisible(false); points.exportLinesDXF()
points.stepLesson(1); points.toggleLesson()
points.exportPLY()
points.render()            // draw one frame (e.g. when the tab is in the background)
```
