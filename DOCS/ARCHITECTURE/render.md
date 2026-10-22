# ARCH:render — `:core-render` entity table

Package `mba.robin.recruiser4d.render`. OpenGL ES 3.0 (`#version 300 es`), instanced quads, CPU depth sort. Android library **without Compose**; only `android.opengl.*`, `java.nio.*`, `android.opengl.GLSurfaceView` interop types.

## §R Normative rendering contract

### §R.1 Shaders (exact sources live as string constants in `SplatShaders`)
- Vertex: per-instance attributes `iPos(vec3)`, `iColor(vec4)`, `iScale(vec3)`; unit quad corners `aCorner(vec2)`; world→clip via `uMVP mat4`; splat projected as an axis-aligned ellipse in view space sized by `iScale` scaled by `1/z_view` and `uViewportHeight·0.5·uFovScale`; output `vColor` and `vEllipse = aCorner` (−1..1 quad uv).
- Fragment: discard where `dot(vEllipse, vEllipse) > 1.0`; alpha falloff `alpha = vColor.a · (1 − dot(vEllipse,vEllipse))^1.5` (Gaussian-like profile); blended with `glBlendFunc(ONE, ONE_MINUS_SRC_ALPHA)` premultiplied; inferred highlight: uniform `uInferredTint vec3` (= #E040FB normalized) blended at `uInferredMix` (0 normally, 0.35 when `highlightInferredSplats` and `iSourceCode==1` passed via `iColor.a` packing trick: separate instanced attribute `iSource float`).
- Clear color per §3 `Backdrop.argb()`.

### §R.2 Sort
Counting sort on 16-bit keys: key = `((viewZ − minZ)/(maxZ − minZ) · 65535)` quantized, descending (far→near draw); cap total splats at `MAX_RENDER_SPLATS` (drop farthest beyond cap, deterministic).

## Entities

| Entity | Type | File | Role | Signature | engaged-by |
|---|---|---|---|---|---|
| `ColorTokens` | object | `src/main/kotlin/mba/robin/recruiser4d/render/ColorTokens.kt` | §3 palette as floats | `val BACKGROUND_COSMIC: FloatArray(4)`, `BACKGROUND_ONYX`, `BACKGROUND_ABYSSAL`, `PRIMARY_CYAN`, `ACCENT_EMERALD`, `SECONDARY_MAGENTA`, `SURFACE_GLASS`; `fun backdropTo(backdrop: Backdrop): FloatArray` | R.1 |
| `SplatShaders` | object | `src/main/kotlin/mba/robin/recruiser4d/render/SplatShaders.kt` | §R.1 GLSL sources | `const val VERTEX_SRC: String`, `const val FRAGMENT_SRC: String` (full compilable ES 3.00 sources) | R.2 |
| `GlProgram` | class | `src/main/kotlin/mba/robin/recruiser4d/render/GlProgram.kt` | Shader program wrapper | `constructor(vertexSrc: String, fragmentSrc: String)`; `fun use(): Unit`; `fun attribute(name: String): Int`; `fun uniform(name: String): Int`; `fun release(): Unit` | R.2 |
| `SplatSorter` | object | `src/main/kotlin/mba/robin/recruiser4d/render/SplatSorter.kt` | §R.2 CPU sort | `fun sortKeys(positions: FloatArray, view: FloatArray): IntArray` (permutation of indices into `positions`) | R.3 |
| `SplatMesh` | class | `src/main/kotlin/mba/robin/recruiser4d/render/SplatMesh.kt` | GPU instanced buffers | `fun upload(splats: List<Splat4D>): Unit` (VBO: per-instance pos12/rgba16/scale12/source4 floats); `fun drawCount(): Int`; `fun bind(program: GlProgram): Unit`; `fun release(): Unit` | R.4 |
| `SplatRenderer` | class | `src/main/kotlin/mba/robin/recruiser4d/render/SplatRenderer.kt` | GLSurfaceView.Renderer | `constructor()`; `fun setWorld(world: SplatWorld): Unit`; `fun setPhase(phase: Float): Unit`; `fun setSettings(settings: WorldSettings): Unit`; `fun setCamera(cam: GlCamera): Unit`; overrides `onSurfaceCreated(gl, config)` (build GlProgram, mesh), `onDrawFrame(gl)` (sort → bind → draw instanced → gizmo overlay), `onSurfaceChanged(gl, w, h)` (viewport, uViewportHeight) | R.5, U.3 |
| `GlCamera` | class | `src/main/kotlin/mba/robin/recruiser4d/render/GlCamera.kt` | Orbit camera math | `var targetX/targetY/targetZ: Float; var distance: Float = 30f; var yawDeg: Float = 45f; var pitchDeg: Float = 20f; fun viewMatrix(): FloatArray (16, column-major); fun perspectiveMatrix(aspect: Float): FloatArray (fovY 60°, near 0.1, far 2000); fun position(): FloatArray(3)` | R.6, U.3 |
| `FrustumGizmo` | class | `src/main/kotlin/mba/robin/recruiser4d/render/FrustumGizmo.kt` | COLMAP-style capture frustum wireframe | `fun draw(program: GlProgram, pose: VignettePose, fovXDeg: Float, depth: Float = 5f): Unit` (8-line wireframe in `SECONDARY_MAGENTA`, own VBO, GL_LINES) | R.7, U.3 |

## Acceptance semantics

- `SplatSorterTest`: 1 000 procedural positions with known view matrix → permutation is descending view-depth order (assert monotonic over sampled keys); re-run → identical permutation (determinism).
- `GlCameraTest`: yaw 0/pitch 0/target origin/distance 10 → `position() == (0,0,10)`; `perspectiveMatrix(1f)[5] ≈ 1/tan(30°)`.
- `SplatShadersTest`: both constants compile under a real EGL context (Robolectric cannot; this is the one androidTest-verified entity: `ShaderCompileInstrumentedTest` on-device) — durable end-state alternative for deviceless passes: `glslangValidator`-style string self-check is NOT invented; instead Accept = source contains `#version 300 es` and balanced braces check via `ShaderCompileCheck.validate(src)` utility in same file (pure Kotlin structural check, honest about what it proves).
- `FrustumGizmoTest`: pose identity, fov 90, depth 5 → the 8 endpoint floats match hand-computed box (±2.5·5/… fixture stated in test).
