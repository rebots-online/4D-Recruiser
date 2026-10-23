# Architecture v2 verification evidence

The sole specification is [ARCHITECTURE.md](../../ARCHITECTURE.md). Files here are reproducible documentation views and validation receipts, not additional planning contracts or application implementation.

- [Validation receipt](validation.json): 87 entity groups, 14 module owners, 489 source lines; table/PlantUML/Mermaid parity, owner/decision references, balanced fences.
- [Render receipt](render-validation.json): actual Mermaid CLI 12.0.0 and PlantUML 1.2026.9 SVG generation; XML parsed and all 87 IDs found in both AST renders.
- [Mermaid solution AST](solution-ast-mermaid.svg), [PlantUML declaration tree](solution-ast-plantuml.svg), [workflow](workflow.svg).

Run from the repository root with Python:

```powershell
python DOCS/verification/architecture-v2/verify_architecture.py
```

After intentionally changing the table, regenerate embedded views with `--refresh`, then render the emitted `.mmd` and `.puml` inputs again. Mermaid commands use `mmdc -i INPUT.mmd -o OUTPUT.svg`; PlantUML uses `java -jar plantuml.jar -tsvg INPUT.puml`. Keep the two AST output names distinct: `solution-ast-mermaid.svg` and `solution-ast-plantuml.svg`. Chromium is required by Mermaid CLI. Tool binaries are external tooling and are not shipped with this repository.

These checks establish document consistency and renderability. They do not establish mathematical correctness, tested dependency compatibility, performance, application functionality, visual UI acceptance, or physical-device operation. The architecture explicitly leaves TC12 UI source export/operator clearance unresolved. No new checklist or application code was produced; the architecture hold remains in effect.
