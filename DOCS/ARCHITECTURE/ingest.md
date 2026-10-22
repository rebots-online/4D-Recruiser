# ARCH:ingest — `:feature-ingest` entity table

Package `mba.robin.recruiser4d.ingest`. All math is closed-form and deterministic (no RNG, no ML model files); identical input bytes → identical splat output, which is what makes ingest tests swarm-safe.

## §I Algorithms (normative)

### §I.1 Luminance
`L(u,v) = (0.2126·R + 0.7152·G + 0.0722·B) / 255` on the ARGB `Int` pixels of the input `Bitmap`.

### §I.2 Pseudo-depth
`d(u,v) = depthScale · clamp(0.7·(1 − L(u,v)) + 0.3·(v/H), 0.05, 1.0)`

### §I.3 Lifting
- Focal: `f = (W/2) / tan(fovX/2)`; fovX from telemetry `fovDegrees` (radians).
- **Perspective** (`PERSPECTIVE_FRUSTUM`), sampled on grid step `GRID_STEP_PX` (u,v ∈ {0, s, 2s, …} < W/H):
  `Z = d·f · (W/2)`; `X = (u − W/2)·Z/f`; `Y = (H/2 − v)·Z/f`; scale `sx=sy=sz = GRID_STEP_PX·Z/f·0.6`; normal `(0,0,−1)`; velocity `v=0`; `wavePhase=0`; `colorPulse=0`; `alpha=0.9`; source `CAPTURED_VIGNETTE`; rgb from pixel.
- **Equirect** (`SPHERICAL_SHELL`): `θ = 2π·(u/W) − π`; `φ = π/2 − π·(v/H)`; `dir = (cosφ·sinθ, sinφ, cosφ·cosθ)`; pos `= dir · DEFAULT_SHELL_RADIUS_M`; scale `sx=sy=sz=0.35f`; all other fields as above.

### §I.4 Lighting estimate
Take pixels with `L` in the top 1 % (sort or histogram threshold; deterministic either way). Centroid of their (x,y) offsets from image center → screen vector `(dx,dy)` with `|dx|,|dy| ≤ 1` after dividing by (W/2, H/2). `lightAzimuthDeg = atan2(dx, dy)·180/π` normalized to (−180,180]; `lightElevationDeg = clamp((1 − meanL_top1)·90, 0, 90)`; `lightColorHex = "#RRGGBB"` (uppercase) of the mean RGB of those pixels; `exposureBias = meanL_all − 0.5` rounded to 3 decimals.

### §I.5 Temporal motion solve (video)
For K keyframes (K=8) each lifted to a splat list *registered by grid index* (same grid → same splat count N; index i in frame k corresponds to index i in frame 0): for each i: `p̄₀` = frame-0 position, `v_i = (p̄_{K−1} − p̄₀) / 2` clamped magnitude ≤ 1.0 m/s; `wavePhase_i = 0`; `colorPulse_i = clamp((maxC_k − minC_k)/255, 0, 0.2)` where C_k = frame k's luminance of i. Output: frame-0 splats with `vx,vy,vz` and `colorPulse` filled, `isAnimated=true`.

### §I.6 Pose proposal (deterministic)
Given `existing: List<SplatVignetteEntity>` sorted by title and this vignette's telemetry:
`idx = existing.size`; `posX = (idx % 4) · 8.0f`; `posY = floor(idx / 4f) · 3.2f` (deck rows, deck height 3.2 m); `posZ = 0f`; `yaw = telemetry.lightAzimuthDeg − 90` normalized to (−180,180]; `pitch = 0`; `roll = 0`; `scale = 1`; `depthScale = 1`. If EXIF GPS altitude tag exists (`GPSAltitude`), `posY = altitude` instead (metres).

## Entities

| Entity | Type | File | Role | Signature | engaged-by |
|---|---|---|---|---|---|
| `ExifTelemetryReader` | object | `src/main/kotlin/mba/robin/recruiser4d/ingest/ExifTelemetryReader.kt` | Still-image EXIF → telemetry | `fun readStill(context: Context, uri: Uri): VignetteTelemetry` — ExifInterface tags: `FocalLength` (mm; default 4.25), `GPSImgDirection`/`GPSAltitude` cached in returned telemetry's azimuth, else `VignetteTelemetry.DEFAULT`; `fovDegrees = 2·atan(36/(2·focalLengthMm))·180/π` clamped 30–120 | I.1 |
| `VideoMetaReader` | object | `src/main/kotlin/mba/robin/recruiser4d/ingest/VideoMetaReader.kt` | Video metadata | `data class VideoMeta(width:Int, height:Int, durationMs:Long, fps:Float, rotationDeg:Int)`; `fun readVideo(context: Context, uri: Uri): VideoMeta` (MediaMetadataRetriever; fps from `METADATA_KEY_CAPTURE_FRAMERATE` else 30f) | I.2 |
| `PseudoDepthEstimator` | object | `src/main/kotlin/mba/robin/recruiser4d/ingest/PseudoDepthEstimator.kt` | §I.2 depth map | `fun estimate(bitmap: Bitmap, depthScale: Float): FloatArray` (row-major W·H, no stride padding) | I.3 |
| `LightingEstimator` | object | `src/main/kotlin/mba/robin/recruiser4d/ingest/LightingEstimator.kt` | §I.4 lighting | `fun estimate(bitmap: Bitmap): VignetteTelemetry` | I.4 |
| `SplatLifter` | object | `src/main/kotlin/mba/robin/recruiser4d/ingest/SplatLifter.kt` | §I.3 pixel→splat | `fun liftPerspective(bitmap: Bitmap, depth: FloatArray, fovXDegrees: Float): List<Splat4D>`; `fun liftEquirect(bitmap: Bitmap): List<Splat4D>` | I.5 |
| `VideoKeyframeExtractor` | object | `src/main/kotlin/mba/robin/recruiser4d/ingest/VideoKeyframeExtractor.kt` | Uniform keyframes | `fun extract(context: Context, uri: Uri, keyframeCount: Int = 8): List<Bitmap>` ( MediaMetadataRetriever.getFrameAtTime at `k·duration/(K)` µs·1000, OPTION_CLOSEST_SYNC; bitmaps scaled so max dimension ≤ 512 ) | I.6 |
| `TemporalMotionSolver` | object | `src/main/kotlin/mba/robin/recruiser4d/ingest/TemporalMotionSolver.kt` | §I.5 velocities | `fun solve(frames: List<List<Splat4D>>): List<Splat4D>` (requires all frames same size; returns frame 0 enriched) | I.7 |
| `PoseEstimator` | object | `src/main/kotlin/mba/robin/recruiser4d/ingest/PoseEstimator.kt` | §I.6 pose proposal | `fun proposePose(telemetry: VignetteTelemetry, existing: List<SplatVignetteEntity>): VignettePose` | I.8 |
| `SplatSerializer` | object | `src/main/kotlin/mba/robin/recruiser4d/ingest/SplatSerializer.kt` | `.sw4d` §4.1 I/O | `fun write(out: OutputStream, splats: List<Splat4D>): Unit`; `fun read(input: InputStream): List<Splat4D>` (throws `java.io.IOException("SW4D bad magic")` on wrong magic / version) | I.9, D.8 |
| `VignetteIngestPipeline` | class | `src/main/kotlin/mba/robin/recruiser4d/ingest/VignetteIngestPipeline.kt` | Orchestrates §I into one vignette | `suspend fun ingest(context: Context, uri: Uri, mediaType: MediaType, worldId: String, existing: List<SplatVignetteEntity>): IngestResult`; `data class IngestResult(vignette: SplatVignetteEntity, splats: List<Splat4D>)` — 360 types route to `liftEquirect`; video types run §I.5; telemetry = still: EXIF ∪ lighting; video: `VideoMetaReader` fov default 70 ∪ lighting; `id = UUID.randomUUID().toString()`; `title` = last path segment; `projectionMode` = 360→SPHERICAL_SHELL else PERSPECTIVE_FRUSTUM; `splatFilePath` = §4.2 path | I.10, X.1 |

## Acceptance semantics

- `PseudoDepthEstimatorTest`: 64×64 procedural bitmap, top half value 255, bottom half 0 → depth of top-centre pixel > depth of bottom-centre pixel; exact values asserted against §I.2 computed by hand in the test.
- `SplatSerializerTest`: round-trip 1 000 mixed splats (procedural fixture) with `structuralEquals` element-wise; bad-magic InputStream throws IOException.
- `SplatLifterTest`: 64×48 solid bitmap, fov 90° → splat count `= ceil(48/4)·ceil(64/4)` = 192; center splat `X≈0 ∧ Y≈0`; all `source == CAPTURED_VIGNETTE`.
- `PoseEstimatorTest`: existing sizes 0,1,4,5 → asserts the four §I.6 outputs exactly.
