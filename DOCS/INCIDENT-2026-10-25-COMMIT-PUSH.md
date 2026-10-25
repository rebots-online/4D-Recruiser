# Incident and self-reminder: commit and push each completed change

## Purpose of the correction system

Learn from each concrete mistake by recording the precipitating failure and deriving a self-reminder that applies at the decision point where it could recur. The reminder should nudge the assistant toward the intended action before the same mistake happens again. The system helps the assistant correct its own behavior; its purpose is not to reduce feedback or optimize reporting.

## Precipitating failure

An explicit instruction required immediate commit and push of four remaining files. The assistant began preliminary checks instead of executing publication. When it executed, its command sequence stopped at a no-op commit before reaching push. It pushed separately, then gave a completion response without connecting the four files to their commits and the live remote.

The mistaken decision was treating publication as deferrable work instead of part of completing each change. This leaves completed work vulnerable to interruption until it has been committed and pushed, and leaves its preservation uncertain until verified.

## Actual outcome

Verification established .codegraph-wsl/.gitignore, .codegraph/.gitignore and IMPLEMENTATION_PLAN.md in a2b6cd66524e65a765097d473e5ac3be3c3385ff, and TOOLS/GITKRAKEN/gk_3.1.77_linux_amd64.zip in 6adfa34a8c4cf80f89171bb35b026f86f234692b. Local master and live origin/master matched the latter commit. The four files were preserved remotely. Eventual publication did not correct the habit of delaying it.

## Self-reminder derived from this incident

Trigger: a change is complete, attention is about to shift to another task, or a completion response is about to be sent.

Reminder: Before moving on from a change, commit it, push it, and verify it reached the remote.

Action: stage the intended files including new files, commit immediately, push immediately, and confirm that the remote branch contains the commit. A no-op commit must not skip a required push. If publication fails, keep it as unfinished work and resolve the failure or state its concrete blocker. After an interruption, reconcile files, local commits and the live remote before assuming the work is protected.

## Mistakes made while recording the correction

The assistant saved a generic rule without the precipitating incident, repeatedly announced a correction before executing it, and then framed the record around attribution, repeated intervention and reporting criteria. This obscured the system's purpose: use a specific past failure to nudge the assistant's next relevant decision.

Trigger: a mistake is being corrected or documented.

Reminder: Record what I did wrong and its outcome; derive a concrete self-nudge for the decision that caused it, then carry out the authorized correction now.

For each incident, retain the failure, consequence, correction, trigger and reminder together so the reminder has a clear reason and an actionable target. Judge the corrective action by whether it addresses the underlying failure. Feedback is useful input to learning, not a failure metric to suppress.

## Persistence boundary

This is a committed project incident record. It does not establish that reminders have been installed in an automatic injection mechanism. KStore remains the sole authority for Admin-Manual reminders and the latest Admin-Manual; this file does not replace that authority or claim a KStore update.
