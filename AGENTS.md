# Owner's scope preference

The owner explicitly requested this rule on 2026-10-22:

- Change only what the owner explicitly asks to change.
- Do not make unrelated improvements, redesigns, refactors, updates, or modifications to other parts of SARU or the PC.
- Read and check what is necessary to understand the requested change, but keep edits within the requested scope.
- If completing a request requires changing another feature or expanding the scope, explain the dependency and obtain the owner's permission first.
- Preserve existing settings, API keys, memory, profiles, files, and unrelated behavior.

Apply this preference to subsequent work in this project. A later explicit instruction from the owner can authorize a specific exception.

## GitHub synchronization requested by the owner

The owner authorized automatic GitHub source updates on 2026-10-23.

- After completing and appropriately validating a user-requested SARU update, publish the relevant reviewed application source, documentation and bundled app assets to `udayaraj35/SARU-AI` on GitHub. The owner explicitly chose Public visibility. Routine publication within this scope does not need another confirmation.
- Preserve the repository's current history and any owner-added files. Read the current branch head before writing and use an expected-head check; never force-push over another change.
- Exclude API keys, passwords, authentication/session material, personal settings, memory/conversation databases, task logs, browser profiles, recordings, work outputs, dependency environments and build caches. Review new files and scan changed text for secrets before publication. An installer belongs in a separately prepared release, not an automatic source commit.
- Do not overwrite the current GitHub README with an obsolete local README. Keep current setup information, integration limitations, third-party notices and the source-only nature of the repository accurate.
- Publish completed relevant work, not partial writes, failed builds, unrelated experiments or unfinished tasks. Do not remove remote files automatically when local files disappear.
- When credentials, validation, conflicts or private content prevent publication, preserve local work and report the specific blocker. Never claim GitHub was updated unless the remote commit and uploaded contents were verified.
- The local GitHub sync baseline and scheduling records are workflow state; do not upload them.
