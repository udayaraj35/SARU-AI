# SARU own-app controls — 2.13.0

The reference dashboard remains unchanged. Apps & Tools exposes Open SARU, Hide SARU, Restart SARU, Exit SARU, Close current panel and Self improvement status. The same actions can be requested through text and completed addressed voice turns.

Commands: `open saru`, `hide saru`, `close settings`, `restart saru`, `close saru`, `close improvement studio`. Hiding keeps the floating companion and configured voice session running. Closing SARU exits the process and microphone session; it cannot hear a wake word after exit. Use the desktop shortcut to reopen it. Restart waits for the old process to shut down and refuses to kill a stuck process. Active source edits block exit/restart.

Say `improve saru <requested change>` or `aafu lai improve gara <change>`. The studio stages the request and suggests existing relevant source files, bounded to eight files and the existing source-size limit. Opening/planning no longer demands the owner edit code. Say `generate saru update`, approve sending the selected source, then inspect the actual diff. `saru update status` reports the current operation/proposal. `apply saru update` still requires local owner verification and exact proposal approval. Backups and rollback remain available through `rollback saru update`. Restart loads approved changes.

This is a bounded source-edit workflow, not unrestricted self-rewriting or model retraining. Protected authorization, recovery and installer files remain outside self-edit scope. Validation checks syntax; generated changes are not automatically functionally tested or executed. Provider setup is required for generation, and unavailable operations report their actual status. No real provider-generated change was applied during release testing.
