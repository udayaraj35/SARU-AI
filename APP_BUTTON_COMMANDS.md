# Control SARU buttons and options by voice or text

- list app options: all registered app actions, including non-visible workflow openers
- open option Audio Center (use the exact option name)
- list buttons: currently mapped/enabled native SARU buttons, including numbered image buttons
- press button Save settings / press button 12
- list tabs / select tab Voice
- list settings options / set option voice_rate to 180

Settings field edits are staged, not saved automatically. Use the Save settings button to validate and persist. API keys and security hashes cannot be set through this generic command; use the protected local field.

An explicit owner button/option/tab command now invokes its existing callback directly, without a second generic OK/Cancel prompt. Duplicate button names require a fresh numbered list. Closed, hidden, disabled or ambiguous buttons are refused. Native buttons execute their existing callbacks; security, publishing, code-edit and file reviews are preserved. This does not grant arbitrary Python, shell, external browser or Windows-dialog control.

Custom canvas-only controls need their registered app action or an existing dedicated command. File dialogs and masked owner-code prompts may still require local input. Invoked means the callback was called; only its own result can establish completion. Unsupported/ambiguous requests report an error rather than claiming success.
