# Incident: delayed commit and push, followed by repeated delay in recording the correction

## Precipitating failure

The user reported that Codex crashed and that four files still appeared untracked after restarting the app. The user explicitly demanded immediate commit and push. The assistant first attempted status, history/context, and instruction discovery instead of executing the requested publication. After the user repeated the instruction, the assistant executed staging and commit. Git reported a clean working tree; that command sequence stopped before pushing because the no-op commit returned a nonzero exit code. The assistant then pushed separately and received “Everything up-to-date.” Its initial response did not identify the four files' commits or establish their presence on the live remote.

Later inspection identified three files in a2b6cd66524e65a765097d473e5ac3be3c3385ff (.codegraph-wsl/.gitignore, .codegraph/.gitignore, IMPLEMENTATION_PLAN.md) and the archive TOOLS/GITKRAKEN/gk_3.1.77_linux_amd64.zip in 6adfa34a8c4cf80f89171bb35b026f86f234692b. The live origin/master and local HEAD matched 6adfa34a8c4cf80f89171bb35b026f86f234692b. This established publication at inspection time; it did not explain the restarted app's earlier display or establish the exact timing of the crash relative to publication.

## Repeated failure while correcting it

When the user asked for durable learning and recurrence prevention, the assistant wrote a local memory update but omitted a concrete account of the precipitating incident. When explicitly told to include that incident, the assistant narrated its intention instead of immediately writing and publishing the record. After the user said “You did it again,” the assistant again sent an intention statement before executing. The user had to repeat the correction. The failure was substituting explanation and promises for the already-authorized concrete action.

## Prevention and completion criteria

The user's direct instruction is to commit and push every completed change rather than defer publication until task or session cleanup. For each completed change, stage the intended files including new files, commit, push, and verify the resulting commit on the live remote before starting the next task or claiming completion. A clean/no-op commit must not suppress an otherwise required push. A failed publication remains unfinished work and must be resolved or reported with its actual blocker.

For a reported mistake, record the precipitating event, the assistant's specific wrong decision, observed consequences, evidence and uncertainty, the corrective action, and a verifiable recurrence-prevention step. Execute the authorized correction rather than repeatedly announcing it. Following a crash, reconcile filesystem changes, commit history and live remote state before claiming work is protected.

This is a project incident record of the user's correction, not an Admin-Manual replacement or a claim that KStore was updated. KStore remains the sole authority for Admin-Manual reminders and the latest Admin-Manual. These are workflow completion criteria; no automatic Git hook or background enforcement has been installed.
