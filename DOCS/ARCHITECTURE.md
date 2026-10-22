# 4D-Recruiser — ARCHITECTURE.md (master)

**Project identity (UUIDv8):** `0192f7c4-8a4d-7c1e-9f3a-4d5b8e7c1a42`
**ExternalProjectUUID (hKG):** same as above. **Origin:** Robin L. M. Cheung, MBA.
**Version:** 1.0 · **Date:** 22 October 2026 · **Phase:** greenfield (pre-implementation; no source tree exists yet — nothing to index, CodeGraph initialized at CODE time).
**Status:** ATTESTED COMPLETE end-state snapshot of the **assembled whole** (I-11/TC13 step 5): all six §10 partials are materialized in this commit; the master is attested only in this whole-document state, never mid-pass. No TBD, no placeholders, no "resolved later." Every entity a coder will type is enumerated in §10 partials. Nothing outside this document set may be coded; nothing inside it is undefined. **CodeGraph:** initialized & verified 22 October 2026 (`codegraph status`: initialized=true, state=complete, 0 files/0 nodes — correct greenfield state).

Source of requirements: `IMPLEMENTATION_PLAN.md` (operator-confirmed decisions 1–3, quoted in §1.1). This document supersedes narrative detail in that plan wherever they conflict on a mechanical fact; the plan remains authoritative for intent.

---

## §1 Product

**4D Living Splat World Builder & Multi-Vignette Stitcher** — an Android/Quest 3S app that ingests regular and 360° stills/videos, lifts them into anisotropic 4D Gaussian-splat vignettes, auto-poses them (EXIF/lighting heuristics) with manual 3D placement, loops every video vignette simultaneously at 60 FPS, and generatively synthesizes lighting-matched bridge splats across uncaptured regions (reference world: a living multi-deck cruise ship).

### §1.1 Confirmed operator decisions (binding)

1. **On-device generative splat inpainting & bridge synthesis** — zero cloud, zero external API. All synthesis is the deterministic geometry/lighting math in `ARCH:stitch-temporal`.
2. **Simultaneous continuous ambient looping (4D living world)** — every video vignette animates concurrently; temporal model in `ARCH:stitch-temporal` §T.
3. **Hybrid COLMAP/EXIF auto-pose + manual assembly** — heuristic estimator proposes; sliders/gizmo dispose; re-stitch on every placement change.

### §1.2 Platform commitments (closed)

| Fact | Value |
|---|---|
| applicationId / namespace root | `mba.robin.recruiser4d` |
| Language / UI | Kotlin 2.1.0, Jetpack Compose (BOM 2024.12.01), Material3 |
| minSdk / targetSdk / compileSdk | 29 / 35 / 35 (Quest 3S = Horizon OS Android) |
| JDK / AGP | 17 / 8.7.3 |
| Persistence | Room 2.6.1 (schema §4.2), DataStore 1.1.1 (preferences only) |
| Rendering | OpenGL ES 3.0 custom splat renderer (`:core-render`), no engine dependency |
| Media | `androidx.exifinterface:exifinterface:1.3.7`, `android.media.MediaMetadataRetriever` |
| Tests | JUnit 4.13.2; fixtures generated procedurally in-test (real data, never mocks) |
| Versioning | `version.txt` at repo root, `MAJOR.MINOR` (start `0.1`), never gitignored; versionName reads it via `build.gradle.kts` |
| Ports | none (no network listener exists in this product; I-16 satisfied vacuously) |

## §2 Module map (Gradle)

Dependency rule: arrows point at what a module compiles against; no cycles; `:app` is the only Android application module; all others are `com.android.library` + `kotlin-android` (no Compose outside `:app`, except `:core-render` which is pure non-Compose library).

| Module | Package | Depends on | Purpose |
|---|---|---|---|
| `:core-model` | `mba.robin.recruiser4d.core.model` | — | Splats, poses, enums, settings (pure Kotlin) |
| `:data-room` | `mba.robin.recruiser4d.data.room` | `:core-model` | Room entities/DAOs/db, ModelRepository |
| `:feature-ingest` | `mba.robin.recruiser4d.ingest` | `:core-model` | EXIF/video meta, depth, lighting, lifting, pose, SW4D I/O |
| `:feature-stitch` | `mba.robin.recruiser4d.stitch` | `:core-model` | Boundary analysis, bridge synthesis, harmonization, WorldStitcher |
| `:feature-temporal` | `mba.robin.recruiser4d.temporal` | `:core-model` | AmbientLoopClock, TemporalEvaluator |
| `:core-render` | `mba.robin.recruiser4d.render` | `:core-model` | GLES3 renderer, sorter, shaders, gizmo, camera |
| `:feature-presets` | `mba.robin.recruiser4d.presets` | `:core-model` | CruiseShipPreset and future preset worlds |
| `:app` | `mba.robin.recruiser4d` | all above | Compose UI, ViewModel, playback, DI (ServiceLocator) |

## §3 Normative constants (closed sets)

- Palette (ARGB hex, used verbatim in `:core-render` ColorTokens and `:app` theme): background `#FF0D0F14`, onyx `#FF050508`, abyssal `#FF071A26`, surface glass `#CC131722`, primary cyan `#FF00BFFF`, accent emerald `#FF00FFCC`, secondary magenta `#FFE040FB`.
- Backdrops enum: `DEEP_COSMIC_SLATE | ONYX | ABYSSAL_OCEAN`.
- Media types: `STILL_REGULAR | STILL_360 | VIDEO_REGULAR | VIDEO_360`.
- Projection modes: `PERSPECTIVE_FRUSTUM | SPHERICAL_SHELL`.
- Splat sources: `CAPTURED_VIGNETTE | GENERATIVE_INPAINT`.
- Model types: `glb | ply | splat_world`.
- Default numeric constants live in exactly one place each — see the owning partial's constants block (no duplicated literals in code).
- Typography: headers `letterSpacing = 1.5.sp`; numeric telemetry uses `FontFamily.Monospace`.

## §4 Data formats

### §4.1 `.sw4d` splat file (little-endian)

Header 12 bytes: magic ASCII `SW4D`, `u16 version=1`, `u16 reserved=0`, `u32 splatCount`. Then `splatCount` × 64-byte records:

| Offset | Bytes | Field |
|---|---|---|
| 0 | 12 | `f32 px, py, pz` |
| 12 | 4 | `u8 r, g, b, pad0` |
| 16 | 4 | `f32 alpha` |
| 20 | 12 | `f32 sx, sy, sz` |
| 32 | 12 | `f32 nx, ny, nz` |
| 44 | 12 | `f32 vx, vy, vz` |
| 56 | 4 | `f32 wavePhase` |
| 60 | 4 | `u8 sourceCode (0=CAPTURED,1=GENERATIVE), pad1, pad2, pad3` |

### §4.2 Room schema v1 (exact DDL in `ARCH:data-room` §D)

Tables `models`, `vignettes`, `viewpoints`; FK `vignettes.worldId → models.id ON DELETE CASCADE`, same for `viewpoints.worldId`. Stored splat files: `<filesDir>/worlds/<worldId>/vignettes/<vignetteId>.sw4d`.

### §4.3 WorldSettings JSON (stored in `models.settingsJson`)

`{"bridgeDensity":1.0,"lightingHarmonization":0.8,"highlightInferredSplats":false,"showCameraFrustums":false,"backdrop":"DEEP_COSMIC_SLATE"}` — keys verbatim, kserialised via `org.json.JSONObject` (no extra dependency).

## §5 Algorithms (authoritative forms in partials)

| Algorithm | Owner partial | Summary |
|---|---|---|
| Pseudo-depth from luminance+vertical cue | `ARCH:ingest` §I.2 | `d = depthScale·clamp(0.7·(1−L)+0.3·(v/H), 0.05, 1.0)` |
| Perspective splat lift (pinhole) | `ARCH:ingest` §I.3 | `Z=d·f, X=(u−W/2)·Z/f, Y=(H/2−v)·Z/f`, grid step 4 px |
| Equirect lift (spherical shell) | `ARCH:ingest` §I.3 | θ/φ from u,v; pos = center + R·dir, R=12 m |
| Lighting vector estimate | `ARCH:ingest` §I.4 | brightest 1 % centroid → azimuth/elevation/color/exposure |
| Temporal motion (harmonic loop) | `ARCH:stitch-temporal` §T | `p(t)=p0+v·A·sin(2π(t+φ))`, 4 s base period, 500 ms crossfade |
| EXIF/lighting pose proposal | `ARCH:ingest` §I.6 | deterministic deck-row layout, closed formula |
| Bridge synthesis | `ARCH:stitch-temporal` §S.2 | lerped chain between boundary splat pairs, sine arch, Lab lerp |
| Depth sort | `ARCH:render` §R.2 | 16-bit counting sort on quantized view depth, 500 k cap |

## §6 User workflows (binding UX contract)

1. **Launch** → preset "Living Cruise Ship" world renders with 4 looping vignettes + inferred hull bridges; presets listed in Library tab.
2. **Ingest** → Splat World Builder tab → *Ingest Vignette* → SAF multi-pick (`image/*`, `video/*`) → pipeline (§I) → vignette row appears with telemetry.
3. **Align** → select vignette in Vignette Inspector → sliders X/Y/Z (m, ±500, 0.1 step), Yaw/Pitch/Roll (°, ±180/±90/±180), Scale (0.1–10), FOV (30–120), projection toggle, warmth (0–1) → viewport updates live; re-stitch auto-runs.
4. **Stitch** → *Synthesize & Stitch World* button or auto-stitch toggle → progress via honest-process events (current pair, splats emitted, elapsed).
5. **Explore** → orbit/pinch/wheel; saved viewpoints (add/recall/delete); `4D LIVE LOOP` badge shows animated vignette count + loop phase; captured-vs-inferred highlight toggle; camera frustum gizmo toggle.

UI must obey `DOCS/SPEC_CONVENTIONS/no-placeholder-ui-content.md`: empty panels stay empty; no invented telemetry values.

## §7 Build & versioning

- `settings.gradle.kts` includes exactly the eight modules of §2. Version catalog `gradle/libs.versions.toml` is the only dependency-version source.
- Manual-first: no CI files exist in v1 (per Admin-Manual CI floor — CI encodes a proven recipe later; nothing here scaffolds it prematurely).
- Release artifacts: debug + release APK (`assembleRelease`), versionName from `version.txt`, `versionCode` = MAJOR·10000+MINOR.

## §8 hKG sync protocol (project CLAUDE.md obligation)

At each ✅ milestone: append the hKG/AST sync block defined in `/mnt/f/.claude/CLAUDE.md` to the session record; Neo4j carries `(:Project {uuid:'0192f7c4-…'})-[:CONTAINS_FILE]->(:File)` for every materialized file, plus `(:Module)-[:DEPENDS_ON]->(:Module)` mirroring §2. Qdrant stores this document's vector; PostgreSQL `task_ledger` gets one row per checklist task per attempt (full record shape per `DOCS/TOOLING_CONVENTIONS/task-ledger-postgres.md`). State at authoring time: **not yet populated** (greenfield; population is checklist task X.2, executed when infrastructure is reachable).

## §9 Execution law (order independence — no exceptions)

1. `DOCS/ARCHITECTURE.md` + its §10 partials are the snapshot of the finished product; `DOCS/CHECKLIST--4d-splat-world.md` is the recipe that makes it real.
2. Nothing not in the checklist may be coded; nothing in the checklist is undefined here.
3. Every checklist task is self-contained: it names its Owns (disjoint files), the exact symbols it wires (verbatim from §10 tables), the Do, the Verify command, and an idempotent end-state Accept (SC2/AP-1..5). No task requires another task to have run — like BASIC line numbers, the dependency is anticipated by name and signature, already frozen in §10.
4. Any subset of tasks, any order, any number of agents, one or two passes: the Accept of a dependent module's task is an end-state assertion (`gradlew :<module>:…` exit 0) that becomes and stays true once its module and its imports' modules exist — re-running is side-effect-free.
5. Markers (SC2): `[ ]` not started · `[/]` in progress · `[x]` written, verify command observed exit 0 · `✅` orchestrator semantic attestation only. A commit that records validation flips the marker in the same commit (marker-sync law).
6. Divergences found at attestation: fix coder output or escalate to architect (I-2); never let a coder choose between options — §10 has already chosen.

## §10 Entity tables (exhaustive, per module)

Each partial carries its module's complete enumeration — every entity with exact name, planned `file` (greenfield: path is authoritative, line omitted until CODE populates it), role, signature — plus an **engaged-by** column naming the checklist tasks that wire it, using task IDs verbatim. Checklist tasks cite these names back verbatim.

| Partial | Module(s) | Entities |
|---|---|---|
| [`ARCHITECTURE/core-model.md`](ARCHITECTURE/core-model.md) | `:core-model` | 10 |
| [`ARCHITECTURE/data-room.md`](ARCHITECTURE/data-room.md) | `:data-room` | 8 |
| [`ARCHITECTURE/ingest.md`](ARCHITECTURE/ingest.md) | `:feature-ingest` | 10 |
| [`ARCHITECTURE/stitch-temporal.md`](ARCHITECTURE/stitch-temporal.md) | `:feature-stitch`, `:feature-temporal` | 7 |
| [`ARCHITECTURE/render.md`](ARCHITECTURE/render.md) | `:core-render` | 8 |
| [`ARCHITECTURE/presets-app-ui.md`](ARCHITECTURE/presets-app-ui.md) | `:feature-presets`, `:app` | 20 |

Total: 63 enumerated entities. Adding any entity requires an architecture amendment (§9.6) before a checklist task may cite it.
