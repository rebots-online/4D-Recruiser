# 4D-Recruiser — implementation checklist — v1 (recipe edition)

## Coder instructions — read before any task (GLM greenfield handoff)

- **Canonical root & authority:** repo `/mnt/f/github/4D-Recruiser`, project UUID `0192f7c4-8a4d-7c1e-9f3a-4d5b8e7c1a42`. Truth hierarchy: `IMPLEMENTATION_PLAN.md` (intent) → `DOCS/ARCHITECTURE.md` + `DOCS/ARCHITECTURE/*.md` partials (frozen mechanical contract) → this checklist (your contract). When two documents conflict on a mechanical fact, the partial entity-table row wins.
- **Intended scope:** Android/Quest app per arch §1–§2 — exactly the 8 Gradle modules and 63 entities of the §10 partials. **Exact allowed files:** only paths appearing in a task's `Owns:` list may be created/modified. **Allowed interfaces:** only the signatures in the cited partial rows, verbatim — no extra members, no extra enum values, no extra DDL constraints.
- **Dependencies & execution order:** none required — arch §9 order-independence is law; any task, any order, any number of agents. Import targets are already named and frozen in the partials; code against them by name, never by exploring neighboring modules.
- **Written work vs automated checks vs product acceptance:** `[x]` = files written AND the task's Verify command observed exit 0 (automated). `✅` = orchestrator semantic attestation. X.1 additionally requires **observed product acceptance** (real install, real render loop) — distinguished there explicitly.
- **Forbidden shortcuts:** no mocks, no stub returns, no TODO, no placeholder UI content (empty panels stay empty), no derived DDL, no /tmp or scratch files, no invented names/paths/values, no reading files outside your task's Owns + this checklist.
- **Preservation:** `IMPLEMENTATION_PLAN.md`, `DOCS/`, and existing git history are never modified or deleted; all work is additive.
- **Verification commands:** exactly those in each task's Verify/Accept lines (`./gradlew :<module>:…`); a task verifies only its own module (I-10a).
- **Escalation:** any ambiguity, contradiction, or failing acceptance = record it with evidence in your handoff and continue the nearest literal reading of the partial row (I-6/rule 13) — never pause, never improvise, never reopen architecture.
- **Commit/push:** commit per task as `CHECKLIST: <task-id> <title>` with the marker flip in the same commit; push when a remote is authorized (none yet — Forgejo embargoed; local commits only).

---

Generated **de novo 22 October 2026** from `DOCS/ARCHITECTURE.md` v1 + its §10 partials. ARCHITECTURE.md is the snapshot of the finished product; this file is the recipe that makes it real. Every open task is a **fully self-contained instruction block** — no other task is needed to code any task; everything the block asserts is defined in its cited architecture section or partial entity-table row, which is frozen contract text. Nothing that is not in this file may be coded.

**Census (counted by task block):** 56 `[ ]` · 0 `[x]` · 0 `✅`. G:10 · M:6 · D:6 · I:10 · S:3 · T:2 · R:7 · P:1 · U:8 · X:3.

## Execution protocol

- **Atomic, idempotent, order-independent** (arch §9 — no exceptions). Any subset of tasks, any order, any number of agents, one or two passes. No task requires another task to exist or be complete; imports reference names/signatures already frozen in the partials. A dependent module's Accept becomes true once its imports' tasks have also landed — by design, never a blocker.
- **Disjoint Owns.** Each task's `Owns:` list is the only set of files it may create/modify. Verify checks only this task's own module output (I-10a), never a transitive full build.
- **Verify + Accept observe durable end-state** (SC2/AP-1..5): re-runnable, side-effect-free command exit codes and on-disk artifacts. Never a transient observation, never a manual UI tap, never a `git commit` posing as a Do step. No mocks, no stubs, no placeholder returns (rule 5).
- **Markers (SC2):** `[ ]` not started · `[/]` in progress · `[x]` written AND Verify command observed exit 0 (coder may flip this far) · `✅` orchestrator semantic attestation only, per task. Marker-sync law: the commit that records validation flips this file's marker in the same commit.
- **Attestations (arch §9.5):** every task below names the exact symbols it wires; on completion the coder annotates that symbol's **engaged-by** cell in the cited partial with `<task-id>✓` (verbatim nomenclature) so parallel agents converge.
- Commit per task: `CHECKLIST: <task-id> <title>` (+ attribution line per harness convention). No push target exists yet (Forgejo embargoed); local commits only.
- Ambiguity felt while coding = architecture defect (I-6): record with evidence in the handoff, continue the nearest literal reading of the cited partial row; never invent a name, path, or value not in this file.

Module build template (`T(mod, deps)` — substitute per table; `:app` additionally applies `compose-compiler` plugin, `buildFeatures.compose = true`, and `androidResources = true`):

```kotlin
plugins { id("com.android.library"); id("org.jetbrains.kotlin.android") }
android {
  namespace = "mba.robin.recruiser4d.<seg>"; compileSdk = 35
  defaultConfig { minSdk = 29; consumerProguardFiles("consumer-rules.pro") }
  compileOptions { sourceCompatibility = JavaVersion.VERSION_17; targetCompatibility = JavaVersion.VERSION_17 }
  kotlinOptions { jvmTarget = "17" }
}
dependencies { deps.forEach { implementation(project(it)) }; testImplementation(libs.junit) }
```

| Module | namespace `<seg>` | project deps |
|---|---|---|
| `:core-model` | `core.model` | — |
| `:data-room` | `data.room` | `:core-model`; + `androidx.room:runtime`, `ksp(androidx.room:room-compiler)`, `androidx.room:ktx`, `kotlinx-coroutines-android` |
| `:feature-ingest` | `ingest` | `:core-model`; + `androidx.exifinterface:exifinterface`, `kotlinx-coroutines-android` |
| `:feature-stitch` | `stitch` | `:core-model` |
| `:feature-temporal` | `temporal` | `:core-model` |
| `:core-render` | `render` | `:core-model` |
| `:feature-presets` | `presets` | `:core-model`, `:feature-stitch` |
| `:app` | (root `mba.robin.recruiser4d`) | all seven modules; + compose BOM stack, `activity-compose`, `lifecycle-viewmodel-compose`, `material3` |

---

## Phase G — Gradle scaffolding

- [ ] **G.1 — Root Gradle scaffold** · Owns: `settings.gradle.kts` · arch §2 §7
  Do: create `settings.gradle.kts` with exactly:
  ```kotlin
  pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }
  dependencyResolutionManagement { repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS); repositories { google(); mavenCentral() } }
  rootProject.name = "4D-Recruiser"
  listOf(":core-model", ":data-room", ":feature-ingest", ":feature-stitch", ":feature-temporal", ":core-render", ":feature-presets", ":app").forEach { m ->
      if (rootProject.file(m.substring(1) + "/build.gradle.kts").isFile) include(m)
  }
  ```
  (Conditional include is the order-independence mechanism: any subset of module dirs configures cleanly.)
  Verify: `./gradlew help` exit 0 (works with zero modules present once G.2 lands).
  Accept: re-run `./gradlew help` exit 0; settings byte-equal to above; nothing else modified.

- [ ] **G.2 — Version catalog, root build, wrapper, version.txt** · Owns: `gradle/libs.versions.toml`, `build.gradle.kts`, `version.txt`, `gradle/wrapper/*`, `gradlew`, `gradlew.bat`, `.gitignore` · arch §1.2 §7
  Do: `version.txt` = `0.1`. `build.gradle.kts` = `plugins { id("com.android.application") version libs... apply false; id("com.android.library") ... apply false; id("org.jetbrains.kotlin.android") ... apply false; id("org.jetbrains.kotlin.plugin.compose") ... apply false; id("com.google.devtools.ksp") ... apply false }` using catalog aliases. `gradle/libs.versions.toml`: versions agp=8.7.3, kotlin=2.1.0, ksp=2.1.0-1.0.29, composeBom=2024.12.01, room=2.6.1, exifinterface=1.3.7, junit=4.13.2, activityCompose=1.9.3, lifecycle=2.8.7, coroutines=1.9.0, coreKtx=1.15.0; libraries androidx-core-ktx, androidx-activity-compose, androidx-lifecycle-runtime-ktx, androidx-lifecycle-viewmodel-compose, androidx-room-runtime, androidx-room-ktx, androidx-exifinterface, junit, compose-bom(platform androidx.compose:compose-bom), compose-ui, compose-ui-graphics, compose-ui-tooling-preview, compose-material3; plugins android-application, android-library, kotlin-android, compose-compiler (`org.jetbrains.kotlin.plugin.compose`), ksp (`com.google.devtools.ksp`). `.gitignore`: `.gradle/`, `build/`, `local.properties`, `**/build/`, `.idea/`, `.tmp/`, `*.apk` (version.txt NOT ignored). Wrapper: run `gradle wrapper --gradle-version 8.9 --distribution-type bin`.
  Verify: `./gradlew --version` prints Gradle 8.9, exit 0.
  Accept: wrapper files tracked; `./gradlew --version` exit 0; `version.txt` contains exactly `0.1`.

- [ ] **G.3 — `:core-model` module scaffold** · Owns: `core-model/build.gradle.kts`, `core-model/consumer-rules.pro` (empty) · arch §2
  Do: apply template `T(:core-model, [])`; add `android { testOptions { unitTests.all { it.useJUnit() } } }`.
  Verify: `./gradlew :core-model:tasks` exit 0. Accept: same, re-run exit 0; no source files exist yet.

- [ ] **G.4 — `:data-room` module scaffold** · Owns: `data-room/build.gradle.kts`, `data-room/consumer-rules.pro`, `data-room/schemas/.gitkeep`
  Do: template `T(:data-room, [":core-model"])` + room deps per header table + `android { defaultConfig { ksp { arg("room.schemaLocation", "$projectDir/schemas") } } }`.
  Verify: `./gradlew :data-room:tasks` exit 0. Accept: re-run exit 0.

- [ ] **G.5 — `:feature-ingest` module scaffold** · Owns: `feature-ingest/build.gradle.kts`, `feature-ingest/consumer-rules.pro`
  Do: template `T(:feature-ingest, [":core-model"])` + exifinterface + coroutines. Verify: `./gradlew :feature-ingest:tasks` exit 0. Accept: re-run exit 0.

- [ ] **G.6 — `:feature-stitch` module scaffold** · Owns: `feature-stitch/build.gradle.kts`, `feature-stitch/consumer-rules.pro`
  Do: template `T(:feature-stitch, [":core-model"])`. Verify: `./gradlew :feature-stitch:tasks` exit 0. Accept: re-run exit 0.

- [ ] **G.7 — `:feature-temporal` module scaffold** · Owns: `feature-temporal/build.gradle.kts`, `feature-temporal/consumer-rules.pro`
  Do: template `T(:feature-temporal, [":core-model"])`. Verify: `./gradlew :feature-temporal:tasks` exit 0. Accept: re-run exit 0.

- [ ] **G.8 — `:core-render` module scaffold** · Owns: `core-render/build.gradle.kts`, `core-render/consumer-rules.pro`
  Do: template `T(:core-render, [":core-model"])`. Verify: `./gradlew :core-render:tasks` exit 0. Accept: re-run exit 0.

- [ ] **G.9 — `:feature-presets` module scaffold** · Owns: `feature-presets/build.gradle.kts`, `feature-presets/consumer-rules.pro`
  Do: template `T(:feature-presets, [":core-model", ":feature-stitch"])`. Verify: `./gradlew :feature-presets:tasks` exit 0. Accept: re-run exit 0.

- [ ] **G.10 — `:app` module scaffold** · Owns: `app/build.gradle.kts`, `app/proguard-rules.pro`
  Do: android-application variant of template: `compileSdk 35`, `defaultConfig { applicationId "mba.robin.recruiser4d"; minSdk 29; targetSdk 35; versionCode = 1*10000+1; versionName = File(rootDir, "version.txt").readText().trim() }`, deps per header table (compose BOM `implementation(platform(libs.compose.bom))`, all 7 projects), `buildFeatures { compose = true }`, plugin `compose-compiler`.
  Verify: `./gradlew :app:tasks` exit 0 (AndroidManifest absent is fine at scaffold; AGP 8 tolerates until assemble — if not, create the §U manifest now from U.1 spec and note it). Accept: re-run exit 0.

## Phase M — `:core-model` (cites `ARCHITECTURE/core-model.md` rows verbatim)

- [ ] **M.1 — Enums + CoreDefaults** · Owns: `core-model/src/main/kotlin/mba/robin/recruiser4d/core/model/{CoreDefaults,SplatSource,MediaType,ProjectionMode,Backdrop}.kt` · symbols: `CoreDefaults`, `SplatSource`, `MediaType`, `ProjectionMode`, `Backdrop`
  Do: implement the 12 constants and 4 closed enums exactly per the partial's tables (incl. `SplatSource.code()`, `MediaType.isVideo/is360`, `Backdrop.argb()` returning §3 ARGB longs). No other members.
  Verify: `./gradlew :core-model:compileDebugKotlin` exit 0. Accept: re-run exit 0; enum value sets byte-match the partial (closed — adding a value requires arch amendment).

- [ ] **M.2 — `Splat4D`** · Owns: `core-model/src/main/kotlin/mba/robin/recruiser4d/core/model/Splat4D.kt`, `core-model/src/test/kotlin/mba/robin/recruiser4d/core/model/Splat4DTest.kt` · symbols: `Splat4D`
  Do: data class with the 20 fields in the partial's exact order/types; `structuralEquals` float-exact. Test: two identical instances → true; one field off by least bit → false.
  Verify: `./gradlew :core-model:testDebugUnitTest --tests 'mba.robin.recruiser4d.core.model.Splat4DTest'` exit 0. Accept: re-run exit 0.

- [ ] **M.3 — `VignettePose`** · Owns: `core-model/src/main/kotlin/mba/robin/recruiser4d/core/model/VignettePose.kt`, `core-model/src/test/kotlin/mba/robin/recruiser4d/core/model/VignettePoseTest.kt` · symbols: `VignettePose.toMatrix4x4ColumnMajor`
  Do: per partial; matrix = T·Rz(roll)·Ry(yaw)·Rx(pitch)·S, degrees, column-major. Test asserts the 16 floats of the hand-computed fixture (pos 1,2,3; yaw 90; pitch 0; roll 0; scale 2 → translation column (2,4,6)) to 1e-5.
  Verify: `./gradlew :core-model:testDebugUnitTest --tests '*VignettePoseTest'` exit 0. Accept: re-run exit 0.

- [ ] **M.4 — `VignetteTelemetry`, `LoopSettings`** · Owns: `core-model/src/main/kotlin/mba/robin/recruiser4d/core/model/{VignetteTelemetry,LoopSettings}.kt`, `core-model/src/test/kotlin/mba/robin/recruiser4d/core/model/LoopSettingsTest.kt` · symbols: `VignetteTelemetry.DEFAULT`, `LoopSettings.periodSeconds`
  Do: per partial (companion DEFAULT constants verbatim). Test: periodSeconds = 4.0/loopSpeed for speed in 0.1..4; clamped outside.
  Verify: `./gradlew :core-model:testDebugUnitTest --tests '*LoopSettingsTest'` exit 0. Accept: re-run exit 0.

- [ ] **M.5 — `WorldSettings`** · Owns: `core-model/src/main/kotlin/mba/robin/recruiser4d/core/model/WorldSettings.kt`, `core-model/src/test/kotlin/mba/robin/recruiser4d/core/model/WorldSettingsTest.kt` · symbols: `WorldSettings.toJson/fromJson`
  Do: JSON keys exactly arch §4.3; missing key → `CoreDefaults` default. Test: round-trip equality for all 3 backdrops + both booleans + non-default floats; `{}` parses to all-default instance.
  Verify: `./gradlew :core-model:testDebugUnitTest --tests '*WorldSettingsTest'` exit 0. Accept: re-run exit 0.

- [ ] **M.6 — `SplatWorld`** · Owns: `core-model/src/main/kotlin/mba/robin/recruiser4d/core/model/SplatWorld.kt`, `core-model/src/test/kotlin/mba/robin/recruiser4d/core/model/SplatWorldTest.kt` · symbols: `SplatWorld.countsBySource/aabbMin/aabbMax`
  Do: per partial. Test: 3 captured + 2 generative procedural splats → counts (3,2); aabb of known fixture stated in test.
  Verify: `./gradlew :core-model:testDebugUnitTest --tests '*SplatWorldTest'` exit 0. Accept: re-run exit 0.

## Phase D — `:data-room` (cites `ARCHITECTURE/data-room.md` §D + rows)

- [ ] **D.1 — `ModelItemEntity`** · Owns: `data-room/src/main/kotlin/mba/robin/recruiser4d/data/room/ModelItemEntity.kt` · symbols: `ModelItemEntity`, `toWorldSettings`
  Do: @Entity table `models`, columns exactly §D order/names/types; `toWorldSettings()` = `WorldSettings.fromJson(settingsJson)`.
  Verify: `./gradlew :data-room:compileDebugKotlin` exit 0. Accept: re-run exit 0.

- [ ] **D.2 — `SplatVignetteEntity`** · Owns: `data-room/src/main/kotlin/mba/robin/recruiser4d/data/room/SplatVignetteEntity.kt` · symbols: `SplatVignetteEntity`, `pose/telemetry/loop/mediaType/projection`
  Do: 25 columns exactly §D; mapping funs return the core-model types.
  Verify: `./gradlew :data-room:compileDebugKotlin` exit 0. Accept: re-run exit 0.

- [ ] **D.3 — `SavedViewpointEntity`** · Owns: `data-room/src/main/kotlin/mba/robin/recruiser4d/data/room/SavedViewpointEntity.kt` · symbols: `SavedViewpointEntity`
  Do: columns exactly §D. Verify: `./gradlew :data-room:compileDebugKotlin` exit 0. Accept: re-run exit 0.

- [ ] **D.4 — `ModelItemDao`** · Owns: `data-room/src/main/kotlin/mba/robin/recruiser4d/data/room/ModelItemDao.kt` · symbols: `ModelItemDao`
  Do: the 4 members verbatim from partial (SQL strings byte-equal). Verify: compile exit 0. Accept: re-run exit 0.

- [ ] **D.5 — `SplatVignetteDao` + `SavedViewpointDao`** · Owns: `data-room/src/main/kotlin/mba/robin/recruiser4d/data/room/{SplatVignetteDao,SavedViewpointDao}.kt` · symbols: both DAOs
  Do: members verbatim (3 each). Verify: compile exit 0. Accept: re-run exit 0.

- [ ] **D.6 — `RecruiserDatabase` + `ModelRepository`** · Owns: `data-room/src/main/kotlin/mba/robin/recruiser4d/data/room/{RecruiserDatabase,ModelRepository}.kt` · symbols: `RecruiserDatabase.build`, `ModelRepository` 6 members
  Do: per partial; `saveVignette` writes `.sw4d` via `SplatSerializer.write` to §4.2 path (mkdirs parents) then upserts; `deleteWorld` deletes dir tree. Verify: `./gradlew :data-room:compileDebugKotlin` exit 0 AND `data-room/schemas/mba.robin.recruiser4d.data.room.RecruiserDatabase/1.json` exists containing `models`, `vignettes` (25 columns), `viewpoints`, both indexes. Accept: both re-run/inspect exit 0 (schema artifact = durable end-state per partial).

## Phase I — `:feature-ingest` (cites `ARCHITECTURE/ingest.md`)

- [ ] **I.1 — `ExifTelemetryReader`** · Owns: `feature-ingest/src/main/kotlin/mba/robin/recruiser4d/ingest/ExifTelemetryReader.kt` · symbols: `ExifTelemetryReader.readStill`
  Do: per partial §I row (fov formula + clamp 30–120; defaults from `VignetteTelemetry.DEFAULT`). Verify: compile exit 0. Accept: re-run exit 0.
- [ ] **I.2 — `VideoMetaReader`** · Owns: `feature-ingest/src/main/kotlin/mba/robin/recruiser4d/ingest/VideoMetaReader.kt` · symbols: `VideoMeta`, `readVideo`
  Do: per partial. Verify: compile exit 0. Accept: re-run exit 0.
- [ ] **I.3 — `PseudoDepthEstimator`** · Owns: main + test `PseudoDepthEstimatorTest.kt` under `feature-ingest/src/{main,test}/kotlin/mba/robin/recruiser4d/ingest/` · symbols: `estimate`
  Do: §I.1+§I.2 exactly; output row-major W·H. Test: 64×64 top-255/bottom-0 bitmap, depthScale 1 → assert the two hand-computed §I.2 depths to 1e-4. Verify: `./gradlew :feature-ingest:testDebugUnitTest --tests '*PseudoDepthEstimatorTest'` exit 0. Accept: re-run exit 0.
- [ ] **I.4 — `LightingEstimator`** · Owns: main + test `LightingEstimatorTest.kt` (same dirs) · symbols: `estimate`
  Do: §I.4 exactly. Test: 64×64 bitmap with a white 8×8 corner block on black → asserts azimuth/elevation/hex/exposure hand-computed values. Verify: testDebugUnitTest filtered exit 0. Accept: re-run exit 0.
- [ ] **I.5 — `SplatLifter`** · Owns: main + test `SplatLifterTest.kt` · symbols: `liftPerspective`, `liftEquirect`
  Do: §I.3 exactly. Test per partial acceptance (192 splats etc.). Verify: filtered testDebugUnitTest exit 0. Accept: re-run exit 0.
- [ ] **I.6 — `VideoKeyframeExtractor`** · Owns: main only · symbols: `extract`
  Do: per partial (8 sync frames, max dim ≤ 512). Verify: compile exit 0. Accept: re-run exit 0.
- [ ] **I.7 — `TemporalMotionSolver`** · Owns: main + test `TemporalMotionSolverTest.kt` · symbols: `solve`
  Do: §I.5 exactly (index-registered; |v| ≤ 1 clamp). Test: 2 synthetic frames offset +0.5 m x → v=(0.25,0,0). Verify: filtered test exit 0. Accept: re-run exit 0.
- [ ] **I.8 — `PoseEstimator`** · Owns: main + test `PoseEstimatorTest.kt` · symbols: `proposePose`
  Do: §I.6 exactly. Test: 4 fixture cases per partial acceptance. Verify: filtered test exit 0. Accept: re-run exit 0.
- [ ] **I.9 — `SplatSerializer`** · Owns: main + test `SplatSerializerTest.kt` · symbols: `write`, `read`
  Do: §4.1 byte layout exactly (little-endian; `ByteBuffer.order(LITTLE_ENDIAN)`). Test: 1 000 procedural splats round-trip `structuralEquals` element-wise; `byteArrayOf('S','W','3','D',…)…` magic violation throws `IOException("SW4D bad magic")`. Verify: filtered test exit 0. Accept: re-run exit 0.
- [ ] **I.10 — `VignetteIngestPipeline`** · Owns: main only · symbols: `IngestResult`, `ingest`
  Do: per partial routing table exactly (360→equirect; video→§I.5 with 8 keyframes; telemetry merge rules; id/title/projection/path rules). Verify: compile exit 0. Accept: re-run exit 0.

## Phase S — `:feature-stitch` (cites `ARCHITECTURE/stitch-temporal.md` §S)

- [ ] **S.1 — `BoundaryPair` + `BoundaryAnalyzer`** · Owns: main + test `BoundaryAnalyzerTest.kt` · symbols: both
  Do: §S.1 exactly (AABB pose-transform, 512-stride boundary sampling, min/max distance filters). Test per partial acceptance. Verify: `./gradlew :feature-stitch:testDebugUnitTest --tests '*BoundaryAnalyzerTest'` exit 0. Accept: re-run exit 0.
- [ ] **S.2 — `LabColor` + `BridgeSynthesizer`** · Owns: main + test `BridgeSynthesizerTest.kt` · symbols: `fromRgb`, `toRgb`, `synthesize`
  Do: §S.2+§S.3 exactly (D65 constants; f(t) closed form stated in partial). Test per partial acceptance (19 outputs, arch y≈0.4 at t=0.5, neutral midpoint). Verify: filtered test exit 0. Accept: re-run exit 0.
- [ ] **S.3 — `WorldStitcher`** · Owns: main + test `WorldStitcherTest.kt` · symbols: `stitch`
  Do: per partial (captured pose-transformed + bridge appended; worldLightLab = Lab mean of boundary splats). Test per partial acceptance. Verify: filtered test exit 0. Accept: re-run exit 0.

## Phase T — `:feature-temporal` (§T)

- [ ] **T.1 — `AmbientLoopClock`** · Owns: main + test `AmbientLoopClockTest.kt` · symbols: `phaseAt`
  Do: §T row exactly (mod arithmetic, [0,1)). Test per partial acceptance. Verify: `./gradlew :feature-temporal:testDebugUnitTest --tests '*AmbientLoopClockTest'` exit 0. Accept: re-run exit 0.
- [ ] **T.2 — `TemporalEvaluator`** · Owns: main + test `TemporalEvaluatorTest.kt` · symbols: `evaluate`
  Do: §T.1 exactly incl. crossfade seam blend; non-animated → base positions verbatim. Test per partial acceptance + seam: τ=0.99, period 4 s → output strictly between τ=0.99 and τ=−0.01 evaluations. Verify: filtered test exit 0. Accept: re-run exit 0.

## Phase R — `:core-render` (cites `ARCHITECTURE/render.md` §R)

- [ ] **R.1 — `ColorTokens`** · Owns: main only · symbols: all 8 members
  Do: §3 palette as normalized float arrays (÷255) + `backdropTo`. Verify: `./gradlew :core-render:compileDebugKotlin` exit 0. Accept: re-run exit 0.
- [ ] **R.2 — `SplatShaders` + `GlProgram` + `ShaderCompileCheck`** · Owns: main + unit test `ShaderCheckTest.kt` · symbols: `VERTEX_SRC`, `FRAGMENT_SRC`, `GlProgram`, `ShaderCompileCheck.validate`
  Do: full ES 3.00 sources implementing §R.1 (attribs `aCorner`, `iPos`, `iColor`, `iScale`, `iSource`; uniforms `uMVP`, `uViewportHeight`, `uFovScale`, `uInferredTint`, `uInferredMix`); `ShaderCompileCheck` = pure-Kotlin structural check (version line, brace balance, every declared uniform/attrib referenced ≥ once) — honest about scope per partial. Test runs `validate` on both sources. Verify: filtered testDebugUnitTest exit 0. Accept: re-run exit 0.
- [ ] **R.3 — `SplatSorter`** · Owns: main + test `SplatSorterTest.kt` · symbols: `sortKeys`
  Do: §R.2 counting sort, 16-bit quantized keys, far→near, deterministic ties. Test per partial acceptance (monotonic + identical re-run permutation). Verify: filtered test exit 0. Accept: re-run exit 0.
- [ ] **R.4 — `SplatMesh`** · Owns: main only · symbols: `upload`, `drawCount`, `bind`, `release`
  Do: per partial (per-instance float stride 44 = pos12+rgba16+scale12+source4; instanced quad VAO-less ES3 path). Verify: compile exit 0. Accept: re-run exit 0.
- [ ] **R.5 — `SplatRenderer`** · Owns: main only · symbols: all 4 setters + 3 GLSurfaceView overrides
  Do: per partial: `onDrawFrame` = evaluate temporal positions (phase) → `SplatSorter` → mesh bind/draw → `FrustumGizmo` overlay when `showCameraFrustums` for the selected pose (setter `setSelectedPose(pose: VignettePose?, fovX: Float)` — add exactly this one member) → clear color from `ColorTokens.backdropTo(settings.backdrop)`; inferred tint mix 0.35 iff `highlightInferredSplats`. Verify: compile exit 0. Accept: re-run exit 0.
- [ ] **R.6 — `GlCamera`** · Owns: main + test `GlCameraTest.kt` · symbols: `viewMatrix`, `perspectiveMatrix`, `position`
  Do: per partial (fovY 60°, near 0.1, far 2000, column-major). Test per partial acceptance. Verify: filtered test exit 0. Accept: re-run exit 0.
- [ ] **R.7 — `FrustumGizmo`** · Owns: main + test `FrustumGizmoTest.kt` · symbols: `draw` + its pure vertex math helper `fun frustumLines(pose: VignettePose, fovXDeg: Float, depth: Float): FloatArray`
  Do: per partial (8 lines, magenta). Test asserts `frustumLines` hand-computed fixture. Verify: filtered test exit 0. Accept: re-run exit 0.

## Phase P — `:feature-presets`

- [ ] **P.1 — `CruiseShipPreset`** · Owns: main + test `CruiseShipPresetTest.kt` · symbols: `build`, `vignettePoses`
  Do: §P.1 table exactly (ids, titles, poses, counts ≥ minima, colors, hull filter box, loop settings). Test: `build()` returns ≥ 7 800 captured splats + ≥ 1 generative hull splat; `vignettePoses().keys == setOf(4 ids)`; deterministic — two calls `structuralEquals` on a sampled subset. Verify: `./gradlew :feature-presets:testDebugUnitTest` exit 0. Accept: re-run exit 0.

## Phase U — `:app` (cites `ARCHITECTURE/presets-app-ui.md` §U)

- [ ] **U.1 — App shell** · Owns: `app/src/main/kotlin/mba/robin/recruiser4d/{RecruiserApplication,MainActivity}.kt`, `app/src/main/AndroidManifest.xml` · symbols: `RecruiserApplication`, `ServiceLocator`, `MainActivity`
  Do: per §U rows (manifest per exact spec; no permissions). Verify: `./gradlew :app:compileDebugKotlin` exit 0. Accept: re-run exit 0.
- [ ] **U.2 — Theme** · Owns: `app/src/main/kotlin/mba/robin/recruiser4d/ui/theme/{Color,Theme,Type}.kt` · symbols: 7 color vals, `RecruiserTheme`, `TelemetryMono`
  Do: §U rows verbatim (§3 palette, 1.5.sp tracking). Verify: compile exit 0. Accept: re-run exit 0.
- [ ] **U.3 — Viewport host** · Owns: `app/src/main/kotlin/mba/robin/recruiser4d/ui/{MainViewerScreen.kt, canvas/SplatCanvasHost.kt}` · symbols: `MainViewerScreen`, `SplatCanvasHost`
  Do: per §U rows (AndroidView GLSurfaceView glue, orbit/pinch, per-frame push, frustum overlay hook, layout composition). Verify: compile exit 0. Accept: re-run exit 0.
- [ ] **U.4 — `ModelViewModel`** · Owns: `app/src/main/kotlin/mba/robin/recruiser4d/ModelViewModel.kt`, `app/src/test/kotlin/mba/robin/recruiser4d/ModelViewModelTest.kt` · symbols: `UiState`, `ModelViewModel` 7 members
  Do: per §U.1 contract; 60 Hz phase ticker coroutine; re-stitch on pose/settings change. Test per partial acceptance (in-memory Room + real preset + real stitcher; no mocks). Verify: `./gradlew :app:testDebugUnitTest --tests '*ModelViewModelTest'` exit 0. Accept: re-run exit 0.
- [ ] **U.5 — Studio sidebar + tabs** · Owns: `app/src/main/kotlin/mba/robin/recruiser4d/ui/studio/{StudioSidebar,LibraryTab,WorldBuilderTab,ViewpointsTab,EngineLightingTab}.kt` · symbols: 5 composables
  Do: per §U rows (tab set closed; SAF OpenMultipleDocuments mimes; settings ranges verbatim). Verify: compile exit 0. Accept: re-run exit 0.
- [ ] **U.6 — `VignetteInspector`** · Owns: `app/src/main/kotlin/mba/robin/recruiser4d/ui/studio/VignetteInspector.kt` · symbols: `VignetteInspector`
  Do: §6.3 ranges verbatim; monospace telemetry readouts from `VignetteTelemetry` only (no-placeholder). Verify: compile exit 0. Accept: re-run exit 0.
- [ ] **U.7 — HUD components** · Owns: `app/src/main/kotlin/mba/robin/recruiser4d/ui/hud/{TelemetryHud,LoopBadge}.kt`, `app/src/main/kotlin/mba/robin/recruiser4d/ui/canvas/{PlaybackDock,OrientationGizmo}.kt` · symbols: 4 composables
  Do: per §U rows (pulse alpha formula verbatim; every datum from UiState). Verify: compile exit 0. Accept: re-run exit 0.
- [ ] **U.8 — HUD + inspector wiring into `MainViewerScreen`** · Owns: modify `app/src/main/kotlin/mba/robin/recruiser4d/ui/MainViewerScreen.kt` (the ONLY file U.8 may touch; it is the sole intended collision point and must merge, not replace, prior U.3 content) · symbols: none new
  Do: place TelemetryHud top-center, OrientationGizmo top-right, PlaybackDock bottom-right, VignetteInspector as sidebar detail pane, `4D LIVE LOOP` badge; all fed from `UiState`. Verify: `./gradlew :app:compileDebugKotlin` exit 0. Accept: re-run exit 0.

## Phase X — Integration & continuity (final pass)

- [ ] **X.1 — Release assembly + run gauntlet observation** · Owns: nothing (verification only; per I-19 green ≠ verified behavior)
  Do: `./gradlew assembleDebug assembleRelease`; install debug APK on device/emulator; observe preset world rendering, loop badge animating, ingest of one real photo, one slider re-stitch. Record observed results verbatim in the handoff. Accept: `app/build/outputs/apk/debug/app-debug.apk` and `…/release/app-release-unsigned.apk` exist; re-running assemble is exit 0 (durable). Runtime observations recorded honestly — success or failure — never fabricated.
- [ ] **X.2 — hKG/AST sync** · Owns: `scripts/hkg_sync.py` · arch §8
  Do: script that (a) Cypher-merges Project/Module/File nodes per §8 for every materialized file, (b) writes the task_ledger rows per `DOCS/TOOLING_CONVENTIONS/task-ledger-postgres.md` from `git log --name-only`; connections via env vars `NEO4J_URI`, `NEO4J_AUTH`, `PG_DSN` (never hard-coded). Accept: script exists, `python3 -I scripts/hkg_sync.py --check` exits 0 with infra reachable (or records the observed connection failure honestly — that failure is the handoff content, not a blocker).
- [ ] **X.3 — README** · Owns: `README.md`
  Do: ≤ 60 lines: product one-liner (§1), module map (§2), build commands (§7), doc pointers (ARCHITECTURE.md, CHECKLIST, TEST pointers). No invented capabilities. Accept: file exists; every command it names exits 0 when run.
