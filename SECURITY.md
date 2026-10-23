# Security

API keys use current-user Windows DPAPI. A process running as the same user may still access keys; this is not protection against a compromised Windows account. Legacy plaintext settings migrate only after encryption succeeds. Migration deliberately avoids an extra plaintext backup. PINs use the existing salted PBKDF2 format. In-process throttling is not a Windows authentication boundary.

Never commit AppData, settings.json, memory.db, tokens or logs. Voice recognition sends requested audio to its recognition service; AI/file summaries send content to the selected provider. No continuous background recording is enabled by default.

The update checksum verifies integrity only, not publisher identity. Signed release verification and rollback are pending; never treat staging as a trusted automatic updater.
