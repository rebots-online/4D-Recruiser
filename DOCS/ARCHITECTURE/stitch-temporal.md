# ARCH:stitch-temporal — `:feature-stitch` + `:feature-temporal` entity tables

## §S `:feature-stitch` — package `mba.robin.recruiser4d.stitch`

### §S.1 Boundary analysis
A vignette's **boundary splats** are its splats whose distance to any *other* vignette's AABB (world-space, from `SplatWorld.aabbMin/aabbMax` after pose transform) is ≤ `BRIDGE_MAX_PAIR_DIST_M`. A **boundary pair** `(a, b)` is any (a from vignette A, b from vignette B, A ≠ B) with `BRIDGE_MIN_PAIR_DIST_M ≤ |a − b| ≤ BRIDGE_MAX_PAIR_DIST_M`. To bound work: sample boundary splats per vignette at stride ⌈count/512⌉ before pairing.

### §S.2 Bridge synthesis (per pair)
`n = clamp(round(bridgeDensity · |a−b| / BRIDGE_STEP_M), 0, BRIDGE_MAX_CHAIN)`; for `i ∈ 1..n−1`, `t = i/n`:
- `pos = lerp(a.pos, b.pos, t)`; `pos.y += sin(π·t) · BRIDGE_ARCH_M · 0.5`
- scale = `lerp(a.scale, b.scale, t) · 0.7`; normal = normalized `lerp(a.n, b.n, t)`; alpha = `lerp(a.α, b.α, t) · 0.85`
- color: convert a,b endpoints' RGB → CIE-Lab (D65, standard closed-form), lerp in Lab, convert back, then §S.3 harmonize
- velocity: `v = (b.pos − a.pos)/|b.pos − a.pos| · 0.05` (gentle flow along the bridge); `wavePhase = t` (travelling wave); `colorPulse = 0.1`
- source = `GENERATIVE_INPAINT`

### §S.3 Lighting harmonization
Blend each bridge splat's Lab color toward the world's mean boundary lighting Lab color by factor `lightingHarmonization ∈ [0,1]` (from `WorldSettings`).

## §S Entities

| Entity | Type | File | Role | Signature | engaged-by |
|---|---|---|---|---|---|
| `BoundaryPair` | data class | `src/main/kotlin/mba/robin/recruiser4d/stitch/BoundaryPair.kt` | Pair candidate | `val a: Splat4D, val b: Splat4D, val distM: Float` | S.1, S.2 |
| `BoundaryAnalyzer` | object | `src/main/kotlin/mba/robin/recruiser4d/stitch/BoundaryAnalyzer.kt` | §S.1 pairs | `fun findPairs(vignettes: Map<String, List<Splat4D>>, poses: Map<String, VignettePose>): List<BoundaryPair>` (transforms each vignette's splats by its pose matrix first) | S.1, S.4 |
| `LabColor` | object | `src/main/kotlin/mba/robin/recruiser4d/stitch/LabColor.kt` | RGB↔CIE-Lab D65 | `fun fromRgb(r: Int, g: Int, b: Int): FloatArray(3)`; `fun toRgb(lab: FloatArray): IntArray(3)` (clamp 0–255; f(t) = t^(1/3) if t > 0.008856 else 7.787t + 16/116) | S.2 |
| `BridgeSynthesizer` | object | `src/main/kotlin/mba/robin/recruiser4d/stitch/BridgeSynthesizer.kt` | §S.2 chains | `fun synthesize(pairs: List<BoundaryPair>, settings: WorldSettings, worldLightLab: FloatArray): List<Splat4D>` (§S.3 applied inline) | S.2 |
| `WorldStitcher` | object | `src/main/kotlin/mba/robin/recruiser4d/stitch/WorldStitcher.kt` | Whole-world stitch | `fun stitch(worldId: String, title: String, vignettes: Map<String, List<Splat4D>>, poses: Map<String, VignettePose>, settings: WorldSettings): SplatWorld` — captured = pose-transformed vignette splats; bridge = §S.1→§S.2; `worldLightLab` = Lab mean of all boundary splats; output splats = captured + bridge | S.3, X.1 |

## §T `:feature-temporal` — package `mba.robin.recruiser4d.temporal`

### §T.1 Temporal evaluation (normative)
Per vignette with `LoopSettings.isAnimated`: at phase `τ ∈ [0,1)` (from `AmbientLoopClock`),
`p_render = p0 + v · motionAmplitude · sin(2π(τ + wavePhase))`; `c_render = c · (1 + 0.1·colorPulse·sin(2πτ))` (clamp 0–255).
Crossfade (loop seam): if `τ > 1 − CROSSFADE_MS/1000/periodSeconds()`, blend with the evaluation at `τ − 1` by weight `w = (1 − τ)·periodSeconds()/(CROSSFADE_MS/1000)`.

## §T Entities

| Entity | Type | File | Role | Signature | engaged-by |
|---|---|---|---|---|---|
| `AmbientLoopClock` | class | `src/main/kotlin/mba/robin/recruiser4d/temporal/AmbientLoopClock.kt` | One clock for all vignettes | `constructor(periodSeconds: Float)`; `fun phaseAt(epochMs: Long): Float` = `((epochMs % (periodSeconds·1000)) / (periodSeconds·1000))`, in `[0,1)` | T.1, U.4 |
| `TemporalEvaluator` | object | `src/main/kotlin/mba/robin/recruiser4d/temporal/TemporalEvaluator.kt` | §T.1 positions | `fun evaluate(splats: List<Splat4D>, phase: Float, loop: LoopSettings): FloatArray` (output 3N render positions, xyz interleaved; non-animated loop → base positions verbatim) | T.2, R.5 |

## Acceptance semantics

- `BridgeSynthesizerTest`: one pair a=(0,0,0) black, b=(10,0,0) white, density 1 → n=20; assert 19 outputs; output[9] at x≈4.75 with arch y = sin(π·0.5)·0.4 ≈ 0.4; midpoint Lab ≈ neutral; all source==GENERATIVE_INPAINT.
- `BoundaryAnalyzerTest`: two 1-splat vignettes 5 m apart → exactly 1 pair distM≈5; 0.5 m apart → 0 pairs (below min).
- `AmbientLoopClockTest`: period 4 s → phaseAt(0)=0, phaseAt(2000)=0.5, phaseAt(3999)<1, phaseAt(4000)=0.
- `TemporalEvaluatorTest`: splat v=(1,0,0), amplitude 1, τ=0.25 → +1.0 in x (within 1e-4); τ=0 → 0; τ=0.75 → −1.0.
- `WorldStitcherTest`: two adjacent 1-splat vignettes → SplatWorld countsBySource == (2 captured, ≥1 generative).
