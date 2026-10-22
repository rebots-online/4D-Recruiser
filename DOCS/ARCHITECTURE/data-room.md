# ARCH:data-room — `:data-room` entity table

Package `mba.robin.recruiser4d.data.room`. Room 2.6.1, schema version 1, `exportSchema = true` (schemas dir `data-room/schemas`).

## §D Room DDL v1 (authoritative — coders use verbatim; INC-2 case study forbids deriving DDL from DAOs)

```sql
CREATE TABLE models (
  id TEXT NOT NULL PRIMARY KEY,
  title TEXT NOT NULL,
  type TEXT NOT NULL CHECK (type IN ('glb','ply','splat_world')),
  createdAtEpochMs INTEGER NOT NULL,
  settingsJson TEXT NOT NULL
);
CREATE TABLE vignettes (
  id TEXT NOT NULL PRIMARY KEY,
  worldId TEXT NOT NULL,
  title TEXT NOT NULL,
  mediaType TEXT NOT NULL CHECK (mediaType IN ('STILL_REGULAR','STILL_360','VIDEO_REGULAR','VIDEO_360')),
  sourceUri TEXT NOT NULL,
  focalLengthMm REAL NOT NULL, fovDegrees REAL NOT NULL,
  lightAzimuthDeg REAL NOT NULL, lightElevationDeg REAL NOT NULL,
  lightColorHex TEXT NOT NULL, exposureBias REAL NOT NULL,
  posX REAL NOT NULL, posY REAL NOT NULL, posZ REAL NOT NULL,
  yaw REAL NOT NULL, pitch REAL NOT NULL, roll REAL NOT NULL,
  scale REAL NOT NULL, depthScale REAL NOT NULL,
  loopSpeed REAL NOT NULL, motionAmplitude REAL NOT NULL, isAnimated INTEGER NOT NULL,
  projectionMode TEXT NOT NULL CHECK (projectionMode IN ('PERSPECTIVE_FRUSTUM','SPHERICAL_SHELL')),
  splatFilePath TEXT NOT NULL,
  FOREIGN KEY (worldId) REFERENCES models(id) ON DELETE CASCADE
);
CREATE TABLE viewpoints (
  id TEXT NOT NULL PRIMARY KEY,
  worldId TEXT NOT NULL,
  name TEXT NOT NULL,
  camPosX REAL NOT NULL, camPosY REAL NOT NULL, camPosZ REAL NOT NULL,
  camYaw REAL NOT NULL, camPitch REAL NOT NULL,
  createdEpochMs INTEGER NOT NULL,
  FOREIGN KEY (worldId) REFERENCES models(id) ON DELETE CASCADE
);
CREATE INDEX index_vignettes_worldId ON vignettes (worldId);
CREATE INDEX index_viewpoints_worldId ON viewpoints (worldId);
```

## Entities

| Entity | Type | File | Role | Signature | engaged-by |
|---|---|---|---|---|---|
| `ModelItemEntity` | @Entity | `src/main/kotlin/mba/robin/recruiser4d/data/room/ModelItemEntity.kt` | World/mesh library row (`models`) | fields per DDL; `fun toWorldSettings(): WorldSettings` | D.1 |
| `SplatVignetteEntity` | @Entity | `src/main/kotlin/mba/robin/recruiser4d/data/room/SplatVignetteEntity.kt` | Vignette row (`vignettes`) | fields per DDL; `fun pose(): VignettePose; fun telemetry(): VignetteTelemetry; fun loop(): LoopSettings; fun mediaType(): MediaType; fun projection(): ProjectionMode` | D.2, U.4, U.6, X.1 |
| `SavedViewpointEntity` | @Entity | `src/main/kotlin/mba/robin/recruiser4d/data/room/SavedViewpointEntity.kt` | Camera checkpoint row (`viewpoints`) | fields per DDL | D.3, U.9 |
| `ModelItemDao` | @Dao interface | `src/main/kotlin/mba/robin/recruiser4d/data/room/ModelItemDao.kt` | models CRUD | `@Upsert fun upsert(m: ModelItemEntity): Unit; @Query("SELECT * FROM models ORDER BY createdAtEpochMs DESC") fun observeAll(): Flow<List<ModelItemEntity>>; @Query("SELECT * FROM models WHERE id = :id") suspend fun getById(id: String): ModelItemEntity?; @Query("DELETE FROM models WHERE id = :id") suspend fun deleteById(id: String): Unit` | D.4 |
| `SplatVignetteDao` | @Dao interface | `src/main/kotlin/mba/robin/recruiser4d/data/room/SplatVignetteDao.kt` | vignettes CRUD | `@Upsert fun upsert(v: SplatVignetteEntity): Unit; @Query("SELECT * FROM vignettes WHERE worldId = :worldId ORDER BY title") fun observeByWorld(worldId: String): Flow<List<SplatVignetteEntity>>; @Query("SELECT * FROM vignettes WHERE id = :id") suspend fun getById(id: String): SplatVignetteEntity?; @Query("DELETE FROM vignettes WHERE id = :id") suspend fun deleteById(id: String): Unit` | D.5 |
| `SavedViewpointDao` | @Dao interface | `src/main/kotlin/mba/robin/recruiser4d/data/room/SavedViewpointDao.kt` | viewpoints CRUD | `@Upsert fun upsert(v: SavedViewpointEntity): Unit; @Query("SELECT * FROM viewpoints WHERE worldId = :worldId ORDER BY createdEpochMs") fun observeByWorld(worldId: String): Flow<List<SavedViewpointEntity>>; @Query("DELETE FROM viewpoints WHERE id = :id") suspend fun deleteById(id: String): Unit` | D.6 |
| `RecruiserDatabase` | @Database | `src/main/kotlin/mba/robin/recruiser4d/data/room/RecruiserDatabase.kt` | Room db v1 | `@Database(entities=[ModelItemEntity::class, SplatVignetteEntity::class, SavedViewpointEntity::class], version=1, exportSchema=true) abstract class …; abstract fun modelItemDao(): ModelItemDao; abstract fun splatVignetteDao(): SplatVignetteDao; abstract fun savedViewpointDao(): SavedViewpointDao; companion fun build(context: Context): RecruiserDatabase` (Room.databaseBuilder, name `recruiser4d.db`) | D.6 |
| `ModelRepository` | class | `src/main/kotlin/mba/robin/recruiser4d/data/room/ModelRepository.kt` | App-wide data facade | `constructor(db: RecruiserDatabase, filesRoot: File)`; `fun observeWorlds(): Flow<List<ModelItemEntity>>; fun observeVignettes(worldId: String): Flow<List<SplatVignetteEntity>>; suspend fun saveWorld(id: String, title: String, settings: WorldSettings): Unit; suspend fun saveVignette(v: SplatVignetteEntity, splats: List<Splat4D>): Unit` (writes `.sw4d` to `<filesRoot>/worlds/<worldId>/vignettes/<id>.sw4d` via `SplatSerializer`, then upserts row); `suspend fun loadVignetteSplats(id: String): List<Splat4D>?`; `suspend fun deleteWorld(id: String): Unit` (cascades rows; deletes world dir) | D.6, X.1 |

## Acceptance semantics

- Room migration test on Robolectric-free instrumentation-free path is NOT used; instead `RecruiserDatabaseTest` (androidTest) executes §D DDL via `db.openHelper.writableDatabase` and asserts `PRAGMA table_info(vignettes)` returns the 25 columns in order. Accept = androidTest `./gradlew :data-room:connectedDebugAndroidTest` exit 0 **or** (deviceless swarm pass) schema JSON `data-room/schemas/…/1.json` exists and contains all three tables and both indexes verbatim — the schema artifact is the durable end-state either way.
