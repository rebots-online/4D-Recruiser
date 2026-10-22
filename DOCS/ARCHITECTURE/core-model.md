# ARCH:core-model — `:core-model` entity table

Package `mba.robin.recruiser4d.core.model`. Pure Kotlin (`java-library`-style Android library, no Android imports except where noted). Constants object below is the single home of every literal in this module.

## Constants (object `CoreDefaults`)

| Name | Type | Value |
|---|---|---|
| `DEFAULT_SHELL_RADIUS_M` | Float | `12.0f` |
| `DEFAULT_LOOP_PERIOD_S` | `Float` | `4.0f` |
| `CROSSFADE_MS` | `Int` | `500` |
| `DEFAULT_BRIDGE_DENSITY` | `Float` | `1.0f` |
| `DEFAULT_LIGHT_HARMONIZATION` | `Float` | `0.8f` |
| `MAX_RENDER_SPLATS` | `Int` | `500_000` |
| `GRID_STEP_PX` | `Int` | `4` |
| `BRIDGE_MAX_PAIR_DIST_M` | `Float` | `30.0f` |
| `BRIDGE_MIN_PAIR_DIST_M` | `Float` | `1.0f` |
| `BRIDGE_STEP_M` | `Float` | `0.5f` |
| `BRIDGE_ARCH_M` | `Float` | `0.8f` |
| `BRIDGE_MAX_CHAIN` | `Int` | `64` |

## Entities

| Entity | Type | File | Role | Signature / fields | engaged-by |
|---|---|---|---|---|---|
| `SplatSource` | enum | `src/main/kotlin/mba/robin/recruiser4d/core/model/SplatSource.kt` | Closed splat provenance set | `CAPTURED_VIGNETTE, GENERATIVE_INPAINT; fun code(): Int` (0/1) | M.1, I.5, S.3, R.5, P.1 |
| `MediaType` | enum | `src/main/kotlin/mba/robin/recruiser4d/core/model/MediaType.kt` | Closed media classification | `STILL_REGULAR, STILL_360, VIDEO_REGULAR, VIDEO_360; val isVideo: Boolean; val is360: Boolean` | M.1, I.1, U.4 |
| `ProjectionMode` | enum | `src/main/kotlin/mba/robin/recruiser4d/core/model/ProjectionMode.kt` | Closed projection set | `PERSPECTIVE_FRUSTUM, SPHERICAL_SHELL` | M.1, I.4, U.6 |
| `Backdrop` | enum | `src/main/kotlin/mba/robin/recruiser4d/core/model/Backdrop.kt` | Closed viewport backdrop set | `DEEP_COSMIC_SLATE, ONYX, ABYSSAL_OCEAN; fun argb(): Long` (§3 palette) | M.5, R.1, U.5 |
| `Splat4D` | data class | `src/main/kotlin/mba/robin/recruiser4d/core/model/Splat4D.kt` | The 4D Gaussian splat record | `px,py,pz, r,g,b:Int(0..255), alpha, sx,sy,sz, nx,ny,nz, vx,vy,vz, wavePhase, colorPulse: Float, source: SplatSource; fun structuralEquals(o: Splat4D): Boolean` (float-exact compare, no epsilon) | M.1, I.4, S.3, T.2, R.5, P.1 |
| `VignettePose` | data class | `src/main/kotlin/mba/robin/recruiser4d/core/model/VignettePose.kt` | Editable 3D placement | `posX,posY,posZ, yaw,pitch,roll, scale, depthScale: Float; fun toMatrix4x4ColumnMajor(): FloatArray` (T·Rz(roll)·Ry(yaw)·Rx(pitch)·S, degrees in, column-major 16 floats) | M.2, I.7, R.7, U.6, P.1 |
| `VignetteTelemetry` | data class | `src/main/kotlin/mba/robin/recruiser4d/core/model/VignetteTelemetry.kt` | EXIF + lighting readouts | `focalLengthMm, fovDegrees, lightAzimuthDeg, lightElevationDeg: Float, lightColorHex: String, exposureBias: Float; companion DEFAULT(f=4.25f, fov=70f, az=135f, el=45f, "#FFFFFF", 0f)` | M.3, I.2, U.6 |
| `LoopSettings` | data class | `src/main/kotlin/mba/robin/recruiser4d/core/model/LoopSettings.kt` | Temporal loop tuning | `loopSpeed, motionAmplitude: Float, isAnimated: Boolean; fun periodSeconds(): Float = DEFAULT_LOOP_PERIOD_S / loopSpeed.coerceIn(0.1f, 4f)` | M.4, T.1, U.7 |
| `WorldSettings` | data class | `src/main/kotlin/mba/robin/recruiser4d/core/model/WorldSettings.kt` | World synthesis + viewport settings; JSON §4.3 | `bridgeDensity, lightingHarmonization: Float, highlightInferredSplats, showCameraFrustums: Boolean, backdrop: Backdrop; fun toJson(): String; companion fun fromJson(s: String): WorldSettings` (org.json; missing key → constant default above) | M.5, S.4, R.6, U.8 |
| `SplatWorld` | data class | `src/main/kotlin/mba/robin/recruiser4d/core/model/SplatWorld.kt` | Runtime world snapshot | `worldId: String, title: String, settings: WorldSettings, splats: List<Splat4D>; fun countsBySource(): Pair<Int,Int>; fun aabbMin(): FloatArray; fun aabbMax(): FloatArray` | M.6, S.4, R.5, P.1, U.2 |

## Acceptance semantics (I-12 — semantic, never grep)

- `Splat4D.structuralEquals` used by round-trip tests (I.5) and preset tests (P.1).
- `VignettePose.toMatrix4x4ColumnMajor` verified against a hand-computed fixture: pose(pos 1,2,3; yaw 90; pitch 0; roll 0; scale 2; depthScale 1) → translation column (2,4,6) (i.e., pos rotated by Ry(90°) then scaled by 2) — unit test states the exact 16 floats.
- `WorldSettings.toJson`/`fromJson` round-trip property: `fromJson(toJson(x)) == x` for all enum values.
