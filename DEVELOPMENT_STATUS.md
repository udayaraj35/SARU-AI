# SARU 17.1.0 development audit and acceptance status

The supplied MASTER_SPEC.md is the product specification. This is an incremental development release, not full acceptance of its 35 sections.

## Implemented and tested in this session
- Versioned atomic settings store. Legacy plaintext API keys migrate to Windows DPAPI ciphertext. Failed migration preserves the original file; corrupt/newer settings fail visibly rather than silently resetting memory or secrets.
- Real Windows DPAPI encrypt/decrypt round trip. Secrets bind to the current Windows user; do not copy ciphertext to another account expecting it to work.
- Responsive native dashboard buttons, scrollable layout, independent circular portrait and access to original artwork preview.
- Actual Windows GUI smoke: startup, settings/profile/appearance/command/social page routes and back navigation; 890x570, 1280x790, 1600x900 sizing; secure save with isolated synthetic data.
- Existing command action tests, English/Roman Nepali/Devanagari parsing, safe arithmetic, settings migration and corruption tests.

## Implemented, further verification needed
- Separate Desktop/startup shortcut choices; Start Menu option in source installer.
- PIN failed-attempt throttling (five failures, sixty-second in-process cooldown). Existing salted PBKDF2 hashes preserved. No hardcoded PIN.
- API key input masking and numerical settings validation.
- Floating assistant visibility persistence and portrait-to-ICO generation.
- Emergency Stop discards in-flight AI replies and stops sounddevice recording. Requests already on the network may finish; TTS and already launched external applications are not forcibly terminated.
- One microphone recording at a time; selected device used.

## Master specification mapping
| Sections | Status / remaining work |
|---|---|
| 1-2 Identity/rules | Existing identity/assets/data retained; incremental modules added |
| 3 UI | Responsive dashboard delivered; several workflows still use dialogs/top-level windows, full 25-page redesign pending |
| 4 Window controls | Native controls retained; minimize/maximize/manual/multi-monitor and tray acceptance pending |
| 5-6 Avatar/floating | Circular portraits, icon generation, drag/resize/visibility; audio-reactive animation, snapping, tray, full settings pending |
| 7,9 Voice/audio | Push-to-talk and Windows TTS exist; tested hardware conversation, state machine, wake word, VAD, barge-in pending |
| 8 MYRA | Companion guides/install/version/launch tools exist; engine embedding not implemented |
| 10-13 PC/agent | Allowlisted commands and diagnostics; no general multi-step planner or durable resume engine |
| 14 Security | DPAPI keys and salted PIN, throttle; Windows Hello/speaker verification/recovery pending |
| 15-16 Providers/network | Four providers, per-provider keys/models; full model discovery/fallback/status tracking pending |
| 17 Memory | SQLite notes/history preserved; full CRUD/import/retention/restore UI pending |
| 18-21 Social/mail/video | Draft/site workflows only; OAuth/publishing/upload/account authorization pending |
| 22-24 Developer/GitHub/REA | HTML starter and REA companion setup only; no embedded REA/GitHub agent |
| 25 Settings | Existing configuration retained; consolidated sections and permission center pending |
| 26 Installer | Python source installer; standalone signed installer/uninstall acceptance pending |
| 27 Updates | HTTPS/checksum staging only; signed channel/auto install/backup/rollback pending |
| 28 Permissions | Action-specific dialogs; centralized permission registry pending |
| 29-30 Reliability/testing | 11 unit/integration tests and Windows GUI smoke; shutdown races, all hardware and account matrix remain |
| 31-35 Acceptance/release | Source release only; full product acceptance explicitly NOT met |

## Compatibility matrix
Windows 11 on this machine: GUI smoke and DPAPI verified. Microphone, sound, brightness, social accounts, install/uninstall and rollback not verified.
Windows 10: targeted but untested.
Windows 8/8.1: unsupported by this modern Python/dependency baseline. No legacy build supplied.
Unknown future Windows: unverified.

## Priority backlog
1. Provider adapters, cancellable job dispatch, clean shutdown and voice state machine.
2. Memory backup/restore and settings recovery UX, permission/task registry.
3. Hardware tests and audio endpoint integration.
4. OAuth adapters with account-specific publication previews.
5. Signed update metadata, rollback and real installer/uninstaller acceptance.

No user accounts were connected, messages sent, hardware changed, or third-party code installed in this development session. Tests used synthetic secrets and isolated local data.

## 17.2.0 — Neon interface redesign (2026-10-20)
- Rebuilt dashboard as native interactive neon panels: sidebar, circular portrait, decorative animated ring, measured CPU/RAM/disk gauges, actual network adapter state and provider configuration status.
- Volume and first supported display brightness read in a COM-initialized background worker. Sliders apply changes and read back actual values; unsupported devices are disabled. Speaker mute/unmute uses the actual endpoint.
- Replaced the old long Settings form with eight scrollable tabs: AI/API, Voice, Appearance, PC/Audio, Memory, Security, Updates, Tools. Added entered-key show/hide, saved-key removal, microphone device index, greeting customization, reduced motion and floating visibility.
- Added Settings neon scan animation and shared colors for existing workflow windows. Animation is decorative, not claimed to be audio-reactive.
- Fixed COM object cleanup warnings by importing comtypes on the UI thread and using a per-worker apartment.
- Verified 14 automated tests and a real Windows GUI smoke covering all eight Settings tabs, invalid input rejection, encrypted save, five page/back routes and three sizes. Real volume/brightness writes and account/API operations remain untested.
- Network badge reports local adapter status, not a claim of Internet/API connectivity. Social features remain draft workflows. No fake recent-activity records are displayed.

Run run_saru.bat to launch this extracted source with its local venv or Python 3.11. Existing installed copies must be upgraded using install_and_run.bat to show these changes.

## 17.2.1 — Windows installation management
- Source installer registers a per-user SARU AI entry in Control Panel Programs and Features / Windows Installed apps. Registration includes version, location, icon, estimated installed disk size and a PowerShell uninstall command. No admin rights required for the per-user registry key.
- Existing registered location becomes the upgrade destination. A different path is rejected until the previous installation is uninstalled. Existing app files are backed up under .saru-backups before copying updates; settings and memory remain in AppData.
- Manifest-based uninstaller removes managed files, dependencies and matching shortcuts. AppData and unrelated user files are retained. It rejects path traversal and linked/junction trees, and refuses while installed SARU is running.
- SARU Storage & RAM appears in dashboard quick tools and Settings > Memory. It measures application folder bytes, AppData bytes and current process resident RAM separately.
- Windows EstimatedSize is an installation-time KiB estimate; Windows controls its rendering and caching. In-app MiB readings are current. Source folders containing ZIP releases naturally measure larger than installed-only folders.
- Tests: 19 Python tests; PowerShell syntax check and disposable workspace uninstall-helper test. Full production installation, Control Panel launch and interactive uninstall of a real installed copy still require acceptance testing. No existing installation was removed or registered by the tests.
- File-copy failures roll back copied application files. Dependency pip upgrades are not transactional; complete dependency rollback is not implemented.

## Current public release: 1.0.0
The owner requested a public version restart. Earlier 17.x entries above are historical development releases. version.py is the single version source for app title, setup, Control Panel registration, manifests and source ZIP naming. This changes no user database or DPAPI schema and retains the existing Windows uninstall identity for in-place upgrade.

Setup now provides Welcome → Location/shortcuts → Optional API → Review → Progress/Finish with Back and Skip. Skipping leaves provider settings unchanged. Adding a key preserves other keys/settings/memory and encrypts the key; API setup is not a connection validation. If no model is entered or previously selected, choose one in Settings before AI chat.

The supplied image guided the new larger portrait, dark neon sidebar, quick tools, battery and real task activity layout. It is not used as a fake interactive screenshot. The attachment's filesystem path was unavailable for copying; its visible reference was used for the layout. Continuous voice and wake-word are not implemented; push-to-talk remains the working control. Battery-less PCs show N/A.

Verified 23 automated tests, application GUI startup/navigation/resizing and real wizard navigation with mocked install effects. Full installed-copy upgrade, dependency download, Control Panel uninstall and account/hardware acceptance remain pending.

## 1.1.0 Live Voice status
See MYRA_VOICE_FINDINGS.md for the installed-MYRA inspection boundary, independent adapter design, official sources, test evidence and setup steps. New continuous Gemini Live conversation is implemented and tested with synthetic transport/audio; real owner speech/provider testing remains pending. It does not embed MYRA or execute PC commands via live voice. Existing push-to-talk remains available. No MYRA credentials or history were migrated.

## 1.2.0 desktop companion
A SARU AI shortcut was created and verified on this PC's OneDrive Desktop, targeting the current development source launcher using Python311/pythonw.exe. It does not enable Windows startup. Keep the project folder or install via the wizard to move to a permanent registered installation.

The new transparent floating companion uses SARU's own portrait and branding. Idle rotation is decorative; listening/speaking/mute states and level bars are driven by Live Voice events. Click opens the voice page, not hidden recording. Right-click exposes voice/settings/stop/hide/exit. App close with keep-running selected explicitly shows the floating companion so SARU cannot become invisibly hidden.

Installed MYRA ui_reference.png was viewed as a visual reference; no MYRA branding/artwork/code was copied into the product. 30 tests plus actual Windows GUI checks passed. End-to-end owner speech/API acceptance remains pending.

## Current 1.3.0 status — 2026-10-21
This section supersedes older per-release claims about requiring a separate Voice page or Start for every app launch. At the owner's explicit request, this personal build can automatically begin Gemini Live when SARU starts. Settings/installer can disable it; the mic indicator and Stop/Mute remain visible. Missing key/model/dependency/device/network yields an error. No real recording or API session was started during development tests.

Unified bottom conversation now handles both typed text and Live transcriptions. The Live session survives navigating Settings and other pages; it is app-owned and is stopped on complete exit. Text sent during a live conversation uses that same session; local allowlisted commands stay in the local executor. Volume/brightness are inline, renamed social buttons open sites, and old missing portrait paths fall back to the bundled image.

Personal improvement currently means explicit saved preference notes (`remember`, `yaad gara`, `save note`) used as context on subsequent Live starts and text requests. The application does not retrain itself, autonomously alter its own source or silently retain all ambient speech. Live Voice still does not expose PC tools; speak-to-execute PC commands beyond classic push-to-talk is a remaining integration task.

Verified: 33 automated tests, actual Windows GUI with inline chat/no Chat popup/portrait fallback/two inline controls/8 Settings tabs/3 sizes, and wizard Next/Back/Skip/Finish using mocked install effects. Full owner speech, real cloud quota/voice quality, physical control writes and production installation/uninstallation remain pending. The source package is not a signed standalone EXE.

## Current 1.4.0 — side chat and screen-control baseline
Conversation is docked on the right when the window is wide enough, with adaptive bottom chat for narrower layouts. PC Control now displays actual manually captured primary-screen images rather than decorative computer images. Captures remain in memory. The owner can select a point and explicitly confirm one click; the app checks freshness, foreground-window identity, local target-patch stability and DPI coordinate compatibility first.

A separate Ask Gemini action sends the entire approved screenshot and the owner's question to the saved Gemini vision-capable model. The app explains that visible private content would be transmitted and requires confirmation. Returned screen text is not treated as tool instructions; AI analysis does not execute clicks. No background monitoring, OCR-only offline engine, general desktop planner or universal app support is claimed.

Verified: 36 tests, side-chat docking at desktop width, screen-panel construction/navigation, coordinate mapping, stale/changed-window rejection and mocked single-click adapter. Real screen capture/analysis/click against external apps has not been acceptance-tested. Exact color/text/layout matching awaits the new reference image the owner said they would supply.

## Current 1.5.0 — supplied reference dashboard
The exact supplied dashboard.png was inspected and used for the SARU portrait/landscape and logo visual regions. Functional controls are native buttons/sliders/comboboxes with generated gradient backgrounds and drawn icons. Sample CPU/network/activity numbers and fake duplicate title-bar controls were not copied as live UI. The resulting layout preserves the reference hierarchy with Settings pinned at sidebar bottom and Social Media separated from PC Control.

The main image is not a claim that every illustrated feature is integrated. Actual controls include search, voice, text chat drawer/composer, local PC/screen page, file selection/summary, system apps, manual screenshot/clipboard, real measured CPU/RAM/disk, speaker volume, first-display brightness, microphone endpoint gain where supported, mute, provider/model switching, API settings/test, notes, updates, theme and social browser entry points. Apps/account APIs still need their respective installation/authentication. Night Light/Eye Care open Windows settings and do not pretend to apply a direct hardware setting. Unsupported endpoints remain disabled. Automatic social publishing, image generation, autonomous universal desktop operation and signed-update rollback remain outside current acceptance.

Visual review was performed with the Windows computer-use skill against a disposable SARU preview with no real mic/API keys. It identified and led to fixes for excessive photo cropping and button-size growth. 36 automated tests and Windows GUI smoke passed, including sidebar Settings, Social Media, three sliders, portrait fallback, provider switching, chat drawer and resize/navigation. Real account/API speech/screen and physical device writes have not been verified. Full production installation/uninstallation acceptance remains pending.
