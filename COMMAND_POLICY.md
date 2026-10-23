# Explicit owner control policy

Normal app and website opening, native SARU buttons/tabs and ordinary interface/settings controls execute directly from a recognized owner text/voice command. There is no extra generic OK/Cancel. Explicit Windows lock/sleep/shutdown requests use their existing Windows APIs; shutdown retains a 30-second cancellation delay. No power operation is run during tests.

Ambiguous app names/buttons still require a concrete choice. A launch request is not reported as a confirmed opened app until window evidence exists. Explicit WhatsApp Web and WhatsApp in PC requests select different destinations.

The application does not grant itself Windows administrator rights, disable UAC, unlock Windows, override account authorization or bypass device permissions. Source editing, cloud image disclosure and sensitive workflows retain their intrinsic review. App button commands invoke their existing callbacks, not arbitrary Python/shell code.

Password filling is initiated only by the explicit fill password locally command on an HTTPS page with a focused password field. It uses a native masked prompt, does not send the secret through SARU chat/voice/IPC, does not save it in SARU conversation memory, and does not submit the form. Python and website memory cannot be guaranteed physically zeroed. Best-effort marked-secret filtering is not a guarantee for arbitrary unlabelled text; never speak credentials to cloud voice.

Ordinary conversation memory remains enabled when configured. Another Windows user or PC supplies their own API keys and accounts; the installer excludes existing private AppData. Local speaker matching is not owner authentication.

Only exact pre-authorized WhatsApp Business jobs can run unattended. See UNATTENDED_WHATSAPP.md for account, timing, no-retry and delivery limits. Personal WhatsApp Web sending and arbitrary autonomous social-media replies are not claimed.
