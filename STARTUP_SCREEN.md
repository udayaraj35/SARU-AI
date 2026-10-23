# SARU startup screen · 2.8.0

The loading screen uses SARU's portrait in a new desk artwork inspired by the supplied loading photo. The supplied 17-second video was inspected at 0, 3, 6, 9, 12 and 16 seconds for the main layout. Assistant view restores the portrait, system readings, quick tools, recent activity and bottom chat; Office view remains available from the header. The selected home view is saved.

Progress represents seven completed startup checks, not a file-byte count or an arbitrary timer:

1. Tk/Windows interface created.
2. Core Python modules imported.
3. Saved settings loaded and unlocked.
4. Local conversation/notes database opened.
5. Dashboard artwork prepared.
6. Assistant service interfaces configured.
7. Main dashboard built.

The main window stays hidden until these checks finish. Voice/network connections start separately after the interface is ready. Optional tool engines continue to load when used; startup does not scan private documents, load every historical release, or claim cloud models are connected. Failed startup is reported through the existing redacted startup log and error dialog. The splash has an Escape/close cancellation action. No artificial loading delay is added in production.

`preview_startup.py` is a visual QA fixture with isolated temporary data and microphone/cloud calls disabled. It deliberately pauses after the real services check so the 86% view can be inspected; this hold is not part of normal startup. `preview_dashboard.py --fullscreen` checks the main view.

Existing owner profiles, API keys, memories, app-control commands and office jobs are preserved by installation.
