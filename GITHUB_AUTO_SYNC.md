# Automatic GitHub source synchronization

The owner authorized automatic publication of completed SARU updates to the Public repository https://github.com/udayaraj35/SARU-AI on 2026-10-23.

After an update completed in this Codex chat, the agent should validate the relevant change, review the publication diff, scan it for private data, and publish it while preserving current remote history. A Codex chat automation also checks once an hour for completed source changes that have not yet been published. This is a local Codex workflow: the PC must be on, Codex must be running, the project must be available and GitHub access/internet must work. It does not run merely because someone installed SARU and does not modify the installed application's own update behavior.

The scheduled check uses a local baseline to skip unchanged source without creating commits. It waits until files are stable and avoids publishing while another SARU development task is active. It preserves remote-only files and does not automatically delete files. Changes involving an active task, failed validation, unknown files, secrets, conflicting remote edits or an unavailable account remain local for review.

Only reviewed application source, documentation and bundled app artwork are in scope. Credentials, settings, memories, conversations, browser sessions, recordings, task logs, exported work, local workflow state, dependencies and generated installers are excluded. Binary installers need a separately prepared release; source synchronization alone does not publish an executable or make installed copies auto-update.

The current GitHub README remains the publication guide. Historical local README files must not replace it. Third-party sources and asset notices retain their existing terms.
