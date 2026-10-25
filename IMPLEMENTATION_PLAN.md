# 4D Living Splat World Builder & Multi-Vignette Stitcher

Transform the 3D Model Player & Navigator into a **4D Living Gaussian Splat World Builder** capable of ingesting regular and 360° stills and videos, positioning them via EXIF/feature-based COLMAP-style pose estimation and manual 3D spatial placement, continuously looping all animated video vignettes simultaneously, and generatively synthesizing realistic splat bridges across uncaptured regions (such as reconstructing a living, multi-deck cruise ship one animated vignette at a time).

### User Review & Critical Decisions

> [!IMPORTANT]
> The following architectural and UX decisions incorporate your confirmed choices from our clarification step and govern how multi-vignette worlds are constructed, stitched, and animated.

- **Confirmed Decision 1 — On-Device Generative Splat Inpainting & Bridge Synthesis**: Uncaptured gaps between ingested stills and videos are filled locally on-device using geometric depth projection, spherical harmonic color/lighting matching, and procedural structure synthesis—requiring zero cloud latency or external API dependencies.
- **Confirmed Decision 2 — Simultaneous Continuous Ambient Looping (4D Living World)**: Every video vignette (regular or 360° equirectangular) converts into a time-varying 4D Gaussian splat cluster that loops continuously and simultaneously in 3D space, creating a living world where water ripples, crowds move, or ship decks bustle concurrently as you navigate through them.
- **Confirmed Decision 3 — Hybrid COLMAP/EXIF Auto-Pose + Manual Multi-Vignette Assembly**: Ingested media is automatically analyzed for EXIF metadata (focal length, orientation, GPS/compass, exposure), dominant lighting vectors, and feature overlap to estimate initial 3D camera poses, paired with interactive 3D gizmo/coordinate sliders so you can manually position, rotate, and scale individual vignettes (e.g., placing the pool deck, atrium, and bridge onto a unified cruise ship scaffold) and trigger generative splat stitching between them.

---

### 1. Overview & Core Concept

- **What It Does**: Allows users to build and explore dynamic, living 3D worlds composed of multiple spatial vignettes—ingested from regular photos, 360° panoramas, regular video clips, and 360° videos. Instead of viewing isolated static meshes, users assemble multi-vignette worlds where captured regions animate in continuous ambient loops and missing architectural or environmental spans between vignettes are generatively bridged with lighting-matched Gaussian splats.
- **Target Audience / Persona**: Spatial creators, VR/Quest 3S explorers, and 3D world-builders reconstructing large real-world environments (such as a multi-deck cruise ship, resort, or architectural complex) from disparate photo and video captures taken across different locations.
- **Key Value**: Bridges the gap between partial real-world captures and complete navigable 3D environments by combining camera/EXIF pose estimation, manual spatial layout controls, continuous 4D temporal splat playback, and automatic gap-filling synthesis.

---

### 2. User Experience & Visual Design

- **Key User Flows**:
  1. **Living World & Preset Showcase**: Launch directly into an interactive 3D viewport featuring a pre-built **"Living Cruise Ship — Multi-Vignette 4D World"** alongside existing spatial presets, demonstrating multiple simultaneous looping animated splat vignettes (Sun Deck Pool Waves, Grand Atrium Chandelier & Promenade, Navigation Bridge Radar, and Ocean Wake) stitched together by generatively inferred hull and deck splats.
  2. **Multi-Modal Media Ingestion (Stills & Video, Regular & 360°)**: Open the **Splat World Studio** drawer tab and tap **Ingest Vignette** to import one or more regular photos, 360° equirectangular stills, regular videos, or 360° videos. The ingestion pipeline extracts frames, reads EXIF camera/orientation tags, estimates scene depth and ambient lighting vectors, and generates anisotropic Gaussian splats (`XYZ` position, `RGB` color, opacity $\alpha$, scale/covariance, and temporal motion vectors $\Delta XYZ, \Delta RGB$ for video loops).
  3. **COLMAP-Style Auto-Alignment & Manual 3D Deck/Vignette Positioning**:
     - Upon ingestion, the engine runs an automatic pose estimator using EXIF focal/orientation data, color-histogram/feature correspondence, and lighting direction to propose a 3D anchor position `(X, Y, Z)` and rotation `(Yaw, Pitch, Roll)`.
     - Users can select any vignette in the **Vignette Inspector** to manually reposition it in 3D space (e.g., placing a newly captured lounge video at `Deck 8 Aft`), adjust its projection mode (`Perspective Frustum` vs. `360° Spherical Shell`), tweak scale/FOV, and align lighting warmth/intensity.
  4. **Generative Gap-Filling & World Stitching**: Tap **Synthesize & Stitch World** (or toggle auto-stitching) to run the on-device generative splat synthesizer. It analyzes boundary splats, surface normals, elevation contours, and lighting gradients between adjacent vignettes, generating cohesive structural and environmental splats to fill uncaptured corridors, decks, sky domes, or water planes.
  5. **Continuous 4D Ambient Exploration**: Navigate freely through the unified world using touch drag orbit, pinch-to-zoom, or saved viewpoint flights while all video-backed splat vignettes animate continuously and simultaneously at 60 FPS with cross-faded loop boundaries.

- **Visual Identity & Theme**:
  - *Aesthetic Direction*: **High-Precision Spatial Telemetry & Holographic Production Studio**—sleek translucent glassmorphic HUD panels floating over a full-bleed 3D spatial canvas.
  - *Color Palette & Mood*:
    - `--background`: Deep Cosmic Slate (`#0D0F14`) with selectable Onyx (`#050508`) and Abyssal Ocean (`#071A26`) viewport backdrops.
    - `--surface`: Translucent Cockpit Glass (`#CC131722`) with subtle 1dp cyan/emerald specular borders.
    - `--primary`: Electric Telemetry Cyan (`#00BFFF`) for primary spatial controls, camera frustums, and active selection indicators.
    - `--accent`: Bio-Luminescent Emerald (`#00FFCC`) for live 4D animated vignette badges and generative synthesis indicators.
    - `--secondary-accent`: Holographic Magenta (`#E040FB`) for inferred/synthesized bridge splat highlights and COLMAP camera pose frustum gizmos.
  - *Typography & Hierarchy*: Crisp geometric sans-serif headers with wide tracking (`letterSpacing = 1.5.sp`) paired with high-contrast `Monospace` numeric readouts for live `XYZ` coordinates, splat counts, EXIF focal/lighting telemetry, and loop frame counters.
  - *Component Styling & Layout*: Collapsible multi-tab left studio panel (**Library**, **Splat World Builder**, **Navigator Viewpoints**, **Engine & Lighting**) paired with top-center live telemetry HUD, top-right 3D orientation gizmo, and bottom-right quick camera & 4D playback controls.

- **Interactive Feedback & Motion**:
  - Visual 3D camera frustum wireframes and spherical bounds rendered directly in the 3D viewport when a vignette is selected for manual positioning.
  - Real-time pulsing `4D LIVE LOOP` indicator badge showing active temporal vignette count and loop phase.
  - Distinct visual toggle to highlight **Captured Splats** vs. **Generatively Inferred Bridge Splats** so users can inspect how the engine stitched missing regions.

---

### 3. Key Product Decisions & Trade-Offs

- **Decision 1: Hybrid Feature/EXIF Pose Estimation + Manual 3D Vignette Placement**
  - *Chosen Approach*: Combine automatic EXIF & visual feature/lighting alignment (COLMAP-inspired sparse pose estimation) with direct manual `X/Y/Z` and `Yaw/Pitch/Scale` transform sliders and presets per vignette.
  - *Why*: When rebuilding a large, complex environment like a cruise ship from separate vignettes (e.g., pool deck, dining room, promenade), disconnected captures often lack overlapping visual features. EXIF + lighting gives a smart initial orientation and scale, while manual positioning lets the creator place each vignette onto its exact deck and bow-to-stern coordinate before generative stitching bridges the spaces between them.
  - *Alternatives Considered*: Purely automatic feature matching was rejected because non-overlapping rooms/decks cannot be positioned without manual spatial placement.

- **Decision 2: On-Device Anisotropic Gaussian Splat & 4D Temporal Loop Representation**
  - *Chosen Approach*: Represent each vignette as a collection of 3D Gaussian splats carrying spatial coordinates, elliptical scale/orientation, color/opacity, and—for video inputs—multi-keyframe temporal offsets (`Δpos`, `Δcolor`, phase velocity) that interpolate smoothly in a continuous 60 FPS ambient loop.
  - *Why*: Delivers immediate, offline-capable 60 FPS rendering on Android and Meta Quest 3S without waiting on cloud GPU queues, while supporting both 2D perspective projections (regular stills/videos) and 360° equirectangular spherical projections.
  - *Alternatives Considered*: Heavy cloud NeRF/3DGS training pipelines were passed over in favor of fast on-device depth/optical-flow splat lifting and interpolation as requested.

- **Decision 3: Multi-Constraint Generative Splat Inpainting Between Vignettes**
  - *Chosen Approach*: Connect spatially separated vignettes using an on-device generative splat synthesizer that samples boundary splat positions, surface normals, EXIF lighting vectors, and harmonic color gradients to interpolate structural bridges, floors, hulls, and ambient surroundings.
  - *Why*: Ensures that sparse vignettes feel like a cohesive, continuous 3D world rather than floating islands in empty space, while adapting dynamically whenever the user drags or repositions a vignette in 3D space.

---

### 4. Technical Architecture & Data Strategy *(Technical Reference)*

- **Architecture & Component Diagram**:

```
┌────────────────────────────────────────────────────────────────────────────┐
│                        MainViewerScreen (Compose UI)                       │
│  ┌──────────────────────────┐  ┌────────────────────────────────────────┐  │
│  │  Spatial Studio Sidebar  │  │       ThreeDCanvas (4D Viewport)       │  │
│  │  • World Model Library   │  │  • Gaussian Splat Elliptical Renderer  │  │
│  │  • Splat World Builder   │  │  • Continuous 4D Temporal Loop Engine  │  │
│  │  • Vignette Pose Editor  │  │  • Camera Frustum & Pose Gizmo Layer   │  │
│  │  • Viewpoint Navigator   │  │  • Generative Bridge Splat Visualizer  │  │
│  └────────────┬─────────────┘  └───────────────────┬────────────────────┘  │
└───────────────┼────────────────────────────────────┼───────────────────────┘
                │                                    │
                ▼                                    ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                     ModelViewModel (Reactive StateFlows)                   │
│  • Active World / Mesh & 4D Splat Cloud State                              │
│  • Vignettes List, Selected Vignette Pose, & Stitch Parameters             │
│  • Continuous 4D Ambient Clock & Render Layer Controls                     │
└───────────────┬────────────────────────────────────┬───────────────────────┘
                │                                    │
                ▼                                    ▼
┌─────────────────────────────────────┐  ┌───────────────────────────────────┐
│   SplatWorldGenerator & Stitcher    │  │   ModelRepository & Room SQLite   │
│  • EXIF & Lighting Pose Estimator   │  │  • ModelItem (Mesh / 4D World)    │
│  • Still/Video Frame Splat Lifter   │  │  • SplatVignette (Pose, Media,    │
│  • 360° Equirectangular & Frustum   │  │    360/Reg, EXIF, Lighting, Loop) │
│    Depth Projector                  │  │  • SavedViewpoint (Checkpoints)   │
│  • COLMAP-Style Sparse Aligner &    │  └───────────────────────────────────┘
│    Generative Gap-Filling Inpainter │
└─────────────────────────────────────┘
```

- **Data Model & State**:
  - **World Model (`ModelItem`)**: Extended to support `splat_world` type alongside `glb` and `ply`, storing world-level synthesis settings (inpaint density, lighting coherence, hull/scaffold template).
  - **Splat Vignette (`SplatVignette` Entity)**: Persisted in Room and linked to a parent `ModelItem` world. Stores:
    - Media metadata: `title`, `mediaType` (`STILL_REGULAR`, `STILL_360`, `VIDEO_REGULAR`, `VIDEO_360`), `sourceUri`.
    - Extracted EXIF & Lighting telemetry: `focalLengthMm`, `fovDegrees`, `lightAzimuth`, `lightElevation`, `lightColorHex`, `exposureBias`.
    - 3D Spatial Pose (COLMAP-estimated + user-editable): `posX`, `posY`, `posZ`, `yaw`, `pitch`, `roll`, `scale`, `depthScale`.
    - Temporal loop properties: `loopSpeed`, `motionAmplitude`, `isAnimated`.
  - **4D Gaussian Splat (`GaussianSplat4D`)**: Runtime structure holding base 3D position, RGB color, opacity $\alpha$, splat radius/anisotropy, normal vector, source classification (`CAPTURED_VIGNETTE` vs. `GENERATIVE_INPAINT`), and temporal harmonic motion parameters (`velocityVec`, `wavePhase`, `colorPulse`) driven by the continuous ambient clock.

- **Interactive Component & State Mapping**:
  - **Media Ingestion Flow**: Selecting a still or video (regular or 360°) invokes `ExifInterface` (for images) and `MediaMetadataRetriever` (for video keyframes, dimensions, and duration), estimates a pseudo-depth map from luminance/chrominance gradients and vertical perspective cues, lifts pixels into 3D/4D Gaussian splats, estimates initial pose relative to existing vignettes, and saves the `SplatVignette` to Room.
  - **Manual Vignette Pose & Alignment Controls**: Selecting a vignette in the sidebar reveals interactive sliders and quick-nudge controls for `X / Y / Z` offset, `Yaw / Pitch`, `Scale`, and `Projection Mode (Regular Frustum vs. 360° Sphere)`. Adjusting any parameter immediately updates the vignette's splat cluster in the 3D viewport and re-runs the on-device generative bridge stitcher between neighboring vignettes.
  - **Generative Gap-Filling Controls**: Users can adjust **Generative Bridge Density**, **Lighting Harmonization**, and **Highlight Inferred Splats** (which tints generatively synthesized splats or renders them in seamlessly blended natural colors) and toggle **Camera Pose Frustums** to see the COLMAP-style capture cameras inside the 3D scene.
