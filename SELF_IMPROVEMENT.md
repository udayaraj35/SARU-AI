# SARU 2.2.0 — Improve My Code & Design

Open Settings > Updates > Improve SARU, Update Center > Improve SARU, or type `improve saru <your requested change>` in chat. Recognized voice commands can open the same reviewed workflow.

1. Describe the desired behavior/design change and select 1–8 existing SARU source files. Default selection covers dashboard and Settings. Maximum source size is 180,000 characters.
2. Generate a proposal using the configured Gemini/OpenAI/OpenRouter/custom compatible provider and model. The app confirms the selected files/provider before sending source. Runtime settings, saved API credentials, memory, personal files and installed dependencies are not included. A detected saved credential inside selected text/request is rejected.
3. SARU requests exact source-block replacements, rejects ambiguous/stale edits, parses/compiles changed Python source and displays a unified diff. Candidate code is not imported or executed during validation. These are syntax checks, not functional tests or a sandbox.
4. Inspect the diff and approve the exact proposal. The app checks review integrity/current-file hashes, backs up originals and atomically replaces each changed file. A failed apply attempts to restore files already written. Personal settings/memory remain separate.
5. Restart SARU to load changed code and verify the requested behavior. Generated code can still have runtime/behavioral defects; syntax success does not mean the feature works.
6. Use Recent proposals > load change > Roll back to restore the originals, provided no later source edits conflict. Backups/proposal state survive restart under AppData/SARU_AI/improvements.

If a change prevents the main app opening, run `recover_saru.bat` from the installed SARU folder. Its recovery UI imports only the protected improvement core and standard Python modules, not the changed app/UI/voice code. Select the applied proposal, restore its backup and restart SARU. Recovery refuses to overwrite later edits or an invalid backup.

This first implementation edits selected existing top-level .py/.md files. It does not add arbitrary files, install packages, run generated shell commands/tests, hot-reload the running app or automatically approve changes. Credential storage, installation/update/recovery and improvement-control modules are excluded from direct proposals. Existing functional tests are excluded from editing. These scope checks are not a sandbox for arbitrary Python that an owner chooses to approve/run.

Validation: fixture-based source staging/apply/rollback, ambiguous/syntax-broken/stale proposals, protected/outside paths, wrong review digest, CRLF preservation, rollback conflicts, partial-write recovery and saved-secret exclusion. Diff/review/rollback GUI and normal dashboard/Settings were checked without real API calls or applying generated code to the user's app. Live provider-generated proposals still require a valid configured account/model and have not been exercised in this update.
