# SARU AI v17 — Window controls and avatar fix

This update is based on the existing v16 source code. User data stored under `%APPDATA%\SARU_AI` is preserved during normal installation.

## Fixes

- Removed the **fake illustrated minimize/maximize/close buttons** from the top-right corner of the dashboard artwork and from the click map. The **real native Windows title-bar controls** remain; this is intentionally more reliable than drawing custom title bars with Tkinter.
- Window has a sensible minimum size. Native **minimize, maximize/restore, close** buttons work as Windows provides them.
- Closing the app now asks whether to **keep the floating assistant running** or **exit completely**; cancel keeps the app open.
- Corrected missing Pillow imports (`ImageOps`, `ImageDraw`) that prevented the floating SARU photo from rendering and could leave an `S` placeholder.
- Improved fallback label from `S` to `SARU` when a selected avatar file is missing/corrupt.
- Kept MYRA guide integration, Settings, API configuration, memory, installer, photo customization, social media draft workflows, and other v16 features.

## Install

1. Close the currently running SARU, including its floating assistant (use Ctrl+Q in old version if required).
2. Extract the ZIP, run `install_and_run.bat`, choose the **same install directory** used previously.
3. Keep **Create desktop shortcut** selected if you want it refreshed. Restart the new app after installation.
4. The neon custom fake window buttons in the image no longer appear. Use the **single set** in the Windows title bar instead.

This is a **source-based Python package**, not a signed standalone EXE. Windows 8/8.1 and future versions have not been verified. Static picture-based hotspots on alternate dashboard images may not match the artwork. Microphone, live social publishing, and other hardware/account features are not guaranteed.

**Tests performed:** Python syntax compilation and package inspection in a non-Windows environment. Actual Windows desktop GUI behavior, voice devices, installation and shortcuts require testing on a Windows PC.
