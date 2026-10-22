# ARCH:presets-app-ui — `:feature-presets` + `:app` entity tables

## §P `:feature-presets` — package `mba.robin.recruiser4d.presets`

### §P.1 Cruise ship preset (normative geometry, all units metres)
World id `preset-cruise-ship-v1`, title `Living Cruise Ship — Multi-Vignette 4D World`. Four vignettes, each procedurally captured-splat-filled (no media files), plus one generative hull bridge set:

| Vignette id | Title | Pose (pos / yaw° / projection) | Procedural content |
|---|---|---|---|
| `sun-deck-pool` | Sun Deck Pool Waves | (0, 12.8, 0) / 0 / SPHERICAL_SHELL | 2 000 splats: water plane (blue #1A6FB5, sinusoidal v=(0,0,0.15·sin pattern), wavePhase spread 0–1), deck ring (#D8D8DC) |
| `grand-atrium` | Grand Atrium Chandelier & Promenade | (0, 6.4, −4) / 180 / PERSPECTIVE_FRUSTUM | 2 400 splats: chandelier (#FFE9A0, colorPulse 0.15, v radial 0.05), promenade arcs (#C9A87C) |
| `nav-bridge` | Navigation Bridge Radar | (0, 16.0, 18) / 0 / PERSPECTIVE_FRUSTUM | 1 600 splats: radar sweep (#00FFCC wedge, v angular), consoles (#22262E) |
| `ocean-wake` | Ocean Wake | (0, 3.0, 34) / 0 / SPHERICAL_SHELL | 1 800 splats: foam streaks (#E8F4FF, v=(−0.2,0,0) aft flow), sea base #0B3C5D |

Hull bridge: runs `WorldStitcher.stitch` on the four vignettes with default settings and keeps only `GENERATIVE_INPAINT` splats whose AABB intersects the hull box x∈[−9,9], y∈[0,19], z∈[−6,36] — rendered in hull white #E6E9EE after harmonization. Loop settings: `loopSpeed=1, motionAmplitude=1, isAnimated=true` for all four.

| Entity | Type | File | Role | Signature | engaged-by |
|---|---|---|---|---|---|
| `CruiseShipPreset` | object | `src/main/kotlin/mba/robin/recruiser4d/presets/CruiseShipPreset.kt` | §P.1 world | `fun build(): SplatWorld` (deterministic; asserts splat counts ≥ table minima); `fun vignettePoses(): Map<String, VignettePose>` | P.1, U.2, X.1 |

## §U `:app` — package `mba.robin.recruiser4d`

### §U.1 UI state contract (ViewModel StateFlows)
`data class UiState(worlds: List<ModelItemEntity>, activeWorld: SplatWorld?, vignettes: List<SplatVignetteEntity>, selectedVignetteId: String?, settings: WorldSettings, loopPhase: Float, animatedCount: Int, splatCount: Int, isStitching: Boolean)` — every displayed datum traces to a field of this state (no-placeholder rule).

### §U.2 Files

| Entity | Type | File | Role | Signature / content | engaged-by |
|---|---|---|---|---|---|
| `RecruiterApplication` → `RecruiserApplication` | class | `app/src/main/kotlin/mba/robin/recruiser4d/RecruiserApplication.kt` | Manifest app; ServiceLocator | `onCreate()` builds `RecruiserDatabase.build(this)`, `ModelRepository(db, filesDir)`, `VignetteIngestPipeline`; `object ServiceLocator { lateinit var repository: ModelRepository; lateinit var ingest: VignetteIngestPipeline }` | U.1 |
| `MainActivity` | class | `app/src/main/kotlin/mba/robin/recruiser4d/MainActivity.kt` | Single activity | `onCreate` → `setContent { RecruiserTheme { MainViewerScreen(viewModel = viewModel()) } }` | U.1 |
| `Color.kt` | file | `app/src/main/kotlin/mba/robin/recruiser4d/ui/theme/Color.kt` | §3 palette Compose constants | `val CosmicSlate = Color(0xFF0D0F14)` … all 7 | U.2 |
| `Theme.kt` | file | `app/src/main/kotlin/mba/robin/recruiser4d/ui/theme/Theme.kt` | Material3 dark theme | `@Composable fun RecruiserTheme(content: @Composable () -> Unit)` | U.2 |
| `Type.kt` | file | `app/src/main/kotlin/mba/robin/recruiser4d/ui/theme/Type.kt` | Typography | headers `letterSpacing = 1.5.sp`; `val TelemetryMono = FontFamily.Monospace` | U.2 |
| `ModelViewModel` | class | `app/src/main/kotlin/mba/robin/recruiser4d/ModelViewModel.kt` | §U.1 state owner | `val uiState: StateFlow<UiState>`; `fun selectVignette(id: String?)`; `fun updatePose(id: String, pose: VignettePose)` (persists + re-stitches); `fun updateSettings(s: WorldSettings)`; `fun ingest(uris: List<Uri>)`; `fun synthesizeAndStitch()`; `fun saveViewpoint(name: String)`; `fun recallViewpoint(id: String)`; clock ticker: 60 Hz `while(isActive)` loop updating `loopPhase` via `AmbientLoopClock` | U.4, U.6, U.7, X.1 |
| `MainViewerScreen` | @Composable | `app/src/main/kotlin/mba/robin/recruiser4d/ui/MainViewerScreen.kt` | Root layout | `@Composable fun MainViewerScreen(viewModel: ModelViewModel)` — Row(StudioSidebar, SplatCanvasHost); TelemetryHud top-center; orientation gizmo top-right; PlaybackDock bottom-right | U.3, U.8 |
| `SplatCanvasHost` | @Composable | `app/src/main/kotlin/mba/robin/recruiser4d/ui/canvas/SplatCanvasHost.kt` | Viewport interop | `@Composable fun SplatCanvasHost(state: UiState, renderer: SplatRenderer, camera: GlCamera)` — `AndroidView(GLSurfaceView)`; touch drag orbit, pinch scale (→ `camera.distance`), push phase/settings/world each frame; draws `FrustumGizmo` for selected vignette when `showCameraFrustums` | U.3 |
| `StudioSidebar` | @Composable | `app/src/main/kotlin/mba/robin/recruiser4d/ui/studio/StudioSidebar.kt` | Collapsible 4-tab panel | `@Composable fun StudioSidebar(state: UiState, onIngest: (List<Uri>) -> Unit, onSelect: (String?) -> Unit, onPose: (String, VignettePose) -> Unit, onSettings: (WorldSettings) -> Unit, onViewpoint: (String) -> Unit, onSynthesize: () -> Unit)` — tabs Library / Splat World Builder / Navigator Viewpoints / Engine & Lighting | U.5 |
| `LibraryTab` | @Composable | `app/src/main/kotlin/mba/robin/recruiser4d/ui/studio/LibraryTab.kt` | Preset + saved worlds list | `@Composable fun LibraryTab(worlds: List<ModelItemEntity>, onOpen: (String) -> Unit)` — renders only real `state.worlds` rows + the cruise preset row | U.5 |
| `WorldBuilderTab` | @Composable | `app/src/main/kotlin/mba/robin/recruiser4d/ui/studio/WorldBuilderTab.kt` | Ingest + vignette list + Synthesize button | `@Composable fun WorldBuilderTab(vignettes: List<SplatVignetteEntity>, isStitching: Boolean, onIngest, onSelect, onSynthesize)` — SAF picker `ActivityResultContracts.OpenMultipleDocuments` mime `image/*`+`video/*`; progress text = live pair/elapsed from honest-process events | U.4, U.5 |
| `VignetteInspector` | @Composable | `app/src/main/kotlin/mba/robin/recruiser4d/ui/studio/VignetteInspector.kt` | Pose editor (§6.3 ranges verbatim) | `@Composable fun VignetteInspector(vignette: SplatVignetteEntity, telemetry: VignetteTelemetry, onPose: (VignettePose) -> Unit)` — sliders X/Y/Z (−500..500, 0.1), Yaw (−180..180), Pitch (−90..90), Roll (−180..180), Scale (0.1..10), FOV (30..120), ProjectionMode toggle, warmth 0..1 (→ `lightColorHex` tint); monospace telemetry readouts | U.6 |
| `ViewpointsTab` | @Composable | `app/src/main/kotlin/mba/robin/recruiser4d/ui/studio/ViewpointsTab.kt` | Checkpoint list | `@Composable fun ViewpointsTab(viewpoints: List<SavedViewpointEntity>, onSave: (String) -> Unit, onRecall: (String) -> Unit, onDelete: (String) -> Unit)` | U.5 |
| `EngineLightingTab` | @Composable | `app/src/main/kotlin/mba/robin/recruiser4d/ui/studio/EngineLightingTab.kt` | Synthesis + viewport settings | `@Composable fun EngineLightingTab(settings: WorldSettings, onSettings: (WorldSettings) -> Unit)` — Bridge Density (0..2), Lighting Harmonization (0..1), Highlight Inferred toggle, Camera Frustums toggle, Backdrop cycle (closed §3 set) | U.5 |
| `TelemetryHud` | @Composable | `app/src/main/kotlin/mba/robin/recruiser4d/ui/hud/TelemetryHud.kt` | Top-center glass HUD | `@Composable fun TelemetryHud(state: UiState)` — monospace XYZ of camera, splat count, animated vignette count; glass surface `#CC131722` | U.7 |
| `LoopBadge` | @Composable | `app/src/main/kotlin/mba/robin/recruiser4d/ui/hud/LoopBadge.kt` | `4D LIVE LOOP` pulse | `@Composable fun LoopBadge(animatedCount: Int, loopPhase: Float)` — emerald `#00FFCC`, pulsing alpha = `0.6 + 0.4·sin(2π·loopPhase)` | U.7 |
| `PlaybackDock` | @Composable | `app/src/main/kotlin/mba/robin/recruiser4d/ui/canvas/PlaybackDock.kt` | Bottom-right controls | `@Composable fun PlaybackDock(phase: Float, onResetCamera: () -> Unit)` — phase readout (0.00–1.00), reset-camera button | U.7 |
| `OrientationGizmo` | @Composable | `app/src/main/kotlin/mba/robin/recruiser4d/ui/canvas/OrientationGizmo.kt` | Top-right 3D axis hint | `@Composable fun OrientationGizmo(camera: GlCamera)` — Canvas-drawn XYZ axes rotated by camera yaw/pitch | U.7 |
| `AndroidManifest.xml` | file | `app/src/main/AndroidManifest.xml` | Manifest | application `RecruiserApplication`, activity `MainActivity` `exported=true` + launcher intent; no permissions (SAF grants media access) | U.1 |

## Acceptance semantics (§U)

- Compose UI verified by screenshot-free unit semantics where possible: `ModelViewModelTest` on Robolectric/JUnit — fake-free: uses a real in-memory Room (`Room.inMemoryDatabaseBuilder`) + real repository + real `WorldStitcher` + `CruiseShipPreset.build()`; asserts `uiState.first().splatCount > 0`, ingest of a procedurally written PNG in `filesDir` adds a vignette row, `updatePose` re-stitch changes `countsBySource().second`.
- Composables: compile-time + visual contract exercised in X.1 gauntlet (real device/emulator run observing preset world at 60 FPS target).
