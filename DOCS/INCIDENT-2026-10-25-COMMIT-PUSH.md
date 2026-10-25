# Incident: failure to treat publication as part of every completed change

## Objective

Protect completed work against crashes and interruptions by committing and pushing every completed change immediately. Success means the intended files are preserved in a commit available on the remote, and that preservation is verified. Feedback frequency, silence, and apparent satisfaction are not success criteria. A complaint exposes a failure; preventing or discouraging complaints does not fix it.

## Precipitating failure and outcome

On an explicit instruction to commit and push four remaining files immediately, the assistant attempted preliminary checks instead of executing publication. Its subsequent command sequence stopped at a no-op commit before reaching push. It then pushed separately, but its initial completion response did not establish which commits contained the four files or verify them against the live remote. The failure was delayed execution and inadequate evidence that the requested work was protected.

Later verification established .codegraph-wsl/.gitignore, .codegraph/.gitignore and IMPLEMENTATION_PLAN.md in a2b6cd66524e65a765097d473e5ac3be3c3385ff, and TOOLS/GITKRAKEN/gk_3.1.77_linux_amd64.zip in 6adfa34a8c4cf80f89171bb35b026f86f234692b. Local master and live origin/master matched the latter commit. The files were preserved remotely. That eventual outcome does not excuse delaying the publication instruction or the missing initial evidence.

## Failures in the corrective action

The assistant first saved a generic rule without the precipitating incident, then repeatedly described intended documentation before executing it. The initial incident record also emphasized attribution and repeated intervention. That framing risked substituting fewer complaints for the actual objective of protecting work. The correction is to document the assistant's failed decision, its effect on the work, and a prevention criterion tied to repository state.

## Required prevention and evidence

After every completed change, stage the intended files including new files, commit immediately, push immediately, and verify that the remote branch contains the commit before beginning another task or claiming completion. Do not defer publication to session cleanup. A no-op commit must not suppress a required push. A failed push leaves publication incomplete; resolve it within authorization or state the concrete blocker and preserve the local work.

After an interruption, reconcile intended files, local commits and the live remote. A clean working directory alone does not establish remote preservation. Completion evidence must connect the changed files to the commit and the remote branch containing it.

For each failure, document the precipitating action or instruction, the assistant's wrong decision, the consequence for the intended outcome, the executed correction, and a verifiable prevention step. Evaluate prevention against the work's actual state, independently of whether anyone raises the issue. Do not suppress, discount, reframe or discourage feedback to satisfy a completion criterion.

This record defines a workflow obligation, not installed automatic enforcement. KStore remains the sole authority for Admin-Manual reminders and the latest Admin-Manual; this incident record does not replace it.
