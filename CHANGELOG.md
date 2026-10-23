# Changelog

## 17.1.0 development — 2026-10-20
- Add responsive native dashboard and preserve original reference artwork.
- Add Windows DPAPI settings migration, schema versioning and atomic saves.
- Add PIN throttling, masked key input and validated numeric settings.
- Add independent shortcut choices, Start Menu option, icon generation and floating visibility.
- Add scoped emergency stop and overlapping microphone protection.
- Add settings tests and isolated real Windows GUI smoke test.
- Preserve master specification and publish explicit acceptance backlog.

## 17.2.0 — 2026-10-20
- Neon responsive command-center dashboard with live PC readings.
- Real asynchronous speaker/display controls with readback and unsupported-device handling.
- Eight themed Settings tabs with validation, encrypted-key controls and reduced motion.
- Matching styles across existing workflow pages and scoped decorative animations.
- 14 tests and expanded real Windows GUI smoke passed. Hardware writes and authenticated services remain unverified.

## 17.2.1 — 2026-10-20
- Add per-user Windows Installed apps / Control Panel registration and estimated disk size.
- Add bounded manifest-driven uninstaller preserving AppData and unrelated files.
- Detect registered upgrade directory and back up replaced application files.
- Add actual SARU disk/RAM usage display and installation regression tests.

## Public 1.0.0 — 2026-10-20
- Restart public version numbering at 1.0.0 using shared version.py; retain legacy install identity and settings schema for upgrades.
- Replace single-screen installer with Next/Back wizard, optional API key page, Skip, review, progress, Finish and optional launch.
- Store setup API keys through stdin and Windows DPAPI, preserving other provider keys, memory and owner preferences. No automatic provider/API call during setup.
- Update cyberpunk dashboard with larger portrait, quick tool tiles, actual battery reading and recent task activity. Reflow to stacked panels on smaller windows.
- Tests: 23 automated tests plus real Windows setup wizard and application GUI smoke tests. Installation backend effects mocked in wizard smoke; full real installation/uninstallation remains pending.

## 1.1.0 — 2026-10-20
- Inspect installed MYRA 0.3.3 metadata and non-secret configuration; record native-analysis limitations in MYRA_VOICE_FINDINGS.md.
- Add independent Gemini Live speech adapter and explicit voice conversation page, transcripts, PCM meters, Stop/mute and headphones option.
- Add separate cloud model/voice/output settings while preserving Windows push-to-talk/TTS.
- Add Google GenAI SDK requirement and synthetic multi-turn/cancellation tests.
- Fix Tk cleanup from background telemetry by removing global worker-thread garbage collection and widget retention.
- 28 tests plus Windows GUI smoke pass. Actual live provider/hardware speech session remains untested.

## 1.2.0 — 2026-10-20
- Add SARU-branded animated floating companion with transparent circular portrait, real voice state colors/PCM level bars, dragging, edge snapping, virtual-desktop bounds and right-click menu.
- Add floating always-on-top/snap settings; preserve reduced-motion option and portrait customization.
- Floating click opens voice page without recording; explicit Start is required. Navigating away stops the session; stopping indicator waits for cleanup.
- Update dark/red neon styling inspired by the installed MYRA reference image, retaining SARU identity and its own assets.
- Create and verify SARU AI desktop shortcut to the updated source launcher. Development shortcut depends on keeping this folder; installed setup refreshes it to the installation location.
- 30 tests and Windows GUI smoke pass. No actual cloud speech or third-party account execution tested; MYRA internals are not embedded.

## 1.3.0 — 2026-10-21
- Move text chat and live voice transcripts into one persistent bottom conversation area; remove the main Chat popup.
- Keep live voice independent of page navigation, and send typed conversation through the same live session when connected.
- Add owner-requested automatic listening on startup with visible status, Stop/Mute, Settings checkbox and installer option. Missing prerequisites remain visible errors, not simulated listening.
- Show volume and brightness sliders together in the main interface; quick brightness focuses the inline control instead of opening a window.
- Rename social navigation to Facebook, WhatsApp Web and Gmail, opening the appropriate sites.
- Add reliable fallback for missing legacy portrait paths, bold raised controls and shadowed title.
- Add explicit preference-memory commands and feed selected saved notes into new Live sessions. No automatic code rewriting/model training.
- 33 tests, Windows GUI navigation/inline-chat/portrait/resizing checks, and wizard smoke passed. Real microphone/cloud acceptance remains pending.

## 1.4.0 — 2026-10-21
- Dock conversation on the right at desktop widths, retaining a bottom layout on narrow windows. Read transcripts and type text in the same interface.
- Add PC Control with a manual real primary-screen preview, selected-point marker and one-click supervised execution.
- Reject expired previews, changed foreground windows, changed target patches and screen-scaling mismatch before clicking. No automatic AI click execution.
- Add explicit Gemini screen-image analysis with a disclosure/confirmation before transmitting the full image and question. No background screen capture or automatic upload.
- 36 tests and Windows GUI smoke pass. Screen vision provider requests and clicks against actual external applications remain untested. Exact requested color/layout matching awaits the user's new reference photo.

## 1.5.0 — 2026-10-21
- Rebuild the dashboard around the owner's supplied dashboard.png reference: brand/search header, portrait/mountain hero, right-side system/audio/provider panels, quick tools and social rows.
- Use actual rounded gradient buttons with hand-drawn tool/social icons, not a whole-dashboard screenshot click map.
- Pin Settings at the bottom of the left navigation and add a separate Social Media page.
- Keep the bottom composer and reveal chat in a same-window side drawer on Chat/incoming conversation.
- Add real input-endpoint microphone gain where supported, alongside measured speaker volume and display brightness.
- Add inline provider/model selectors, app picker, system tools and explicit Windows Night Light/Eye Care settings actions.
- Fix portrait cropping, intrinsic button sizes and Tk garbage collection on worker threads found during visual/resize review.
- 36 automated tests and Windows GUI smoke passed; source compiles. Hardware writes, external social/account actions and real Gemini voice/vision acceptance remain pending.

## 1.6.0 — 2026-10-21
- Add official WhatsApp Business text sending and Facebook Page text publishing with destination/text review, encrypted tokens and server operation IDs.
- Add social account setup and composer entry points. Keep manual browser drafts available.
- Add opt-in launch/six-hour release checks and automatic checksum-verified downloads from a configured trusted repository; installation remains explicit.
- Match release checksum assets to the selected ZIP; reject invalid release versions/repository inputs.
- Document remaining account setup, incoming-message, personal-account, GitHub skill and unattended-install limitations in SOCIAL_AND_UPDATES.md.

## 1.7.0 — 2026-10-21
- Extend PC Control with running-app window selection and focused screenshot capture.
- Add reviewed double/right click, bounded scroll, Unicode text entry and predefined keyboard shortcuts.
- Preserve the clipboard during Unicode typing; keep corner fail-safe enabled.
- Reject expired screenshots, changed foreground windows, display mismatch and changed target patches before input.
- Add the `pc control` chat command, eight input tests and documented practical limits in PC_CONTROL.md.

## 1.7.1 — 2026-10-21
- Windows event log confirmed repeated pythonw.exe / _ctypes.pyd access violations. Isolate audio/display native COM/WMI operations in a bounded subprocess so helper failures cannot close the dashboard.
- Add reliable launcher, persistent startup/callback diagnostics, fault-handler traces and visible startup error reporting. Route installer/batch startup through the diagnostic launcher.
- Match Settings and other workflow buttons to dashboard rounded gradients, bold text and hover borders.
- Validate dashboard/Settings routes, native-helper crash containment and saved-settings startup. Exact historical native stack remains unavailable; this isolates the suspected device path rather than claiming all native crash causes are identified.

## 1.8.0 — 2026-10-21
- Bridge completed, explicit SARU-prefixed voice commands to the reviewed desktop command router; keep generated assistant speech out of command execution.
- Add Chrome/Edge launch commands and route configured WhatsApp commands into the API composer with recipient/text prefilled. Unconfigured accounts still open honest manual Web drafts.
- Share Warm romantic / Friendly / Professional companion instructions between voice and text. Keep the AI identity and actual action limitations clear.
- Persist completed voice conversations locally when memory is enabled, retain typed Live messages, retrieve related older text context and add `recall <topic>` search. Add a memory preference and companion style control in Settings.
- Voice tools run after a completed model turn and require an on-screen review. No full autonomous tool planner or personal WhatsApp API is added. Connected accounts, valid model/key and relevant external permissions are still required.

## 1.8.1 — 2026-10-21
- Remove the duplicate top search/chat entry; keep one bottom message composer.
- Place chat history at the bottom above the composer on all window sizes.
- Validate Settings/navigation and bottom chat at three window sizes with GUI smoke test.

## 1.8.2 — 2026-10-21
- F11 toggles fullscreen; Escape returns to the normal window. Native maximize/restore remains supported.
- Adapt sidebar and bottom chat/composer insets to window width, size chat height to available height, wrap quick/social tool tiles and add a chat-history scrollbar.
- Refine the shared romantic companion prompt for natural Nepali/Romanized Nepali affection, varied phrasing, contextual questions and practical task-focused responses.
- Validate three window sizes, bottom chat, Settings navigation and fullscreen toggle/exit in the isolated Windows GUI smoke test.

## 1.9.0 — 2026-10-21
- Add persistent Neon Rose, Cyber Violet, Ocean Cyan and Emerald Night palettes across dashboard, Settings, native controls and gradient buttons. Preserve original portrait/art colors.
- Add header Theme picker and Appearance theme selector with immediate application after save.
- Add Male/Female voice presets and a selectable Gemini Live voice list (Aoede, Kore, Puck, Charon, Fenrir). Cloud voice changes require stopping/restarting the voice session; Windows previews require an installed voice.
- Clear a previously pinned Windows voice ID when gender preference changes and avoid matching the substring male inside female.
- Official cloud voice reference: https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/live-api/configure-language-voice
- Validate palette switching in the isolated dashboard GUI smoke test. No paid cloud voice session was used for this release.

## 1.9.1 — 2026-10-21
- Add smooth absolute mouse drag/click and wheel adjustment for audio/display sliders, immediate percentage feedback and throttled live device writes.
- Reuse a crash-isolated native device helper for writes; coalesce queued drag values so only the newest pending value per control is applied. Read back the affected device only.
- Separate writes from telemetry refresh, reject stale responses and protect dragged/pending slider values from background refresh.
- Restore the missing legacy button skin helper found by navigation smoke testing.
- Hardware validation: speaker volume 90→89→90, brightness 69→68→69 and mic gain 81→80→81, with real readback; originals restored and no audio recorded. Measured warm helper readback: brightness ~0.219 s, mic gain ~0.016 s on this PC. First helper startup takes longer; device latency varies.
- Add coalescing/failure tests and synthetic slider-drag GUI verification without changing hardware during UI smoke tests.

## 2.0.0 — 2026-10-21
- Add Video Studio: local photo/caption/audio MP4 rendering and landscape/portrait export, with a preview-first approval workflow.
- Add Google desktop OAuth/PKCE connection, YouTube video uploads, Facebook Page video uploads and TikTok creator-info/direct-post integrations. Keep credentials in existing DPAPI settings.
- Stage and hash exact review copies, bind approval to immutable metadata, check account identity, prevent duplicate claims and retain receipts/uncertain states without automatic retries.
- Add recent draft/status views and account setup. API acceptance is shown separately from confirmed platform publication. Production authentication/publication remains unverified.
- Reduce redundant UI/style work and native device scans; display streamed speech in continuous messages and repair Escape fullscreen handling.
- See VIDEO_AND_PUBLISHING.md for setup, supported limits, validation and known incomplete account requirements.

## 2.1.0 — 2026-10-21
- Preserve the whole source portrait in the dashboard and fit the whole floating portrait inside its circular boundary, replacing face-cropping fits.
- Cache subtle zoom frames; animate only while the actual voice state is listening/speaking. Stopped/muted/error/idle portraits remain static; Reduced motion also disables zoom.
- Enlarge floating labels/right-click menu and add Appearance sliders for desktop portrait (48–240), desktop/menu text (10–22), dashboard portrait size (60–110%) and interface text (90–140%). Save settings applies the preferences; floating portrait/menu apply immediately and dashboard rebuild uses the saved size.
- Debounce portrait resize rendering, preserve virtual-desktop bounds and reuse frames to avoid image resizing on every animation tick.
- Validate 73 unit tests, dashboard/Settings GUI smoke, floating state/menu rendering and non-compounding text scaling.

## 2.2.0 — 2026-10-21
- Add Improve SARU: owner requests and selected-source AI proposals, unified diff review and syntax-only validation without executing candidate code.
- Add integrity/current-source checks, approved bounded writes, backups, partial-apply restoration, persistent proposal history and conflict-aware rollback.
- Add independent recover_saru.bat/recover_saru.py recovery for changes that prevent the main app opening.
- Expose the workflow through Settings Updates, Update Center and `improve saru <request>` commands; keep credentials/personal data and protected update/recovery modules out of proposals.
- Document functional verification limits and account requirements in SELF_IMPROVEMENT.md.
