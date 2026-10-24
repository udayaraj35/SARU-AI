# SARU 2.16 Advanced workspace

Open **Apps & Tools → Advanced workspace**, **Settings → Tools → Advanced workspace**,
or type `open advanced workspace`. The existing SARU dashboard remains the main interface.
Mark LVI's Qt/OpenGL workspace runs in a separate process because its event loop and
dependencies differ from the main Tk app. Opening it pauses the main microphone;
closing it resumes main voice if it was previously enabled. Fully exiting SARU stops both.

## Included source and controls

The owner-supplied Mark component includes its 3D holographic face, facial expressions,
audio/transcript visemes, echo guard, push-to-talk, audio device selection, session
resumption, model fallback, undo, topic monitoring, briefings, telemetry, HUD video,
provider configuration and QR-paired phone dashboard. Avatar graphics depend on the PC's
OpenGL driver. The photo used by the main dashboard remains unchanged.

The source bundle contains 17 discoverable actions: browser_control, code_helper,
computer_control, computer_settings, desktop_control, dev_agent, file_controller,
file_processor, flight_finder, game_updater, open_app, reminder, send_message,
video_player, weather_report, web_search and youtube_video. The workspace builds its
capability descriptions from loaded tools. These tools require appropriate accounts,
apps, media utilities and permissions; inclusion is not an end-to-end acceptance test.
UAC, secure desktops and the lock screen retain Windows restrictions.

## Setup

Use **Install dependencies** to create `.advanced-env` independently of the main app's
environment; then **Install browsers** downloads Chromium and Firefox into private
Advanced storage. The original upstream setup.py is bundled for reference, never run.
First use copies reviewed public source into `%APPDATA%/SARU_AI/advanced/runtime`.

The existing SARU Gemini key, preferred voice and model seed the new Advanced config
once. Later Advanced provider settings are independent. Hold **Ctrl+Space** to speak by
default; text input also works. Optional local wake detection ships as **Hey Jarvis**,
not a trained SARU voice model. Wake detection does not identify a person. Whisper,
Piper and local language models require selecting/installing their packages/models;
ElevenLabs and hosted providers require the owner's own credentials. No proprietary
MYRA engine, model, voice or credentials are included.

## Private storage and review

Advanced config and long-term JSON memory are encrypted at rest using the current
Windows account's DPAPI. They cannot be moved to another account and automatically
decrypted. They are decrypted in process memory while in use. Conversations and actual
tool results are recorded in SARU's existing private journal when automatic memory is
enabled, with the existing sensitive-text filter. Disabling memory prevents recording
and retrieval on subsequent requests; it does not erase existing files or already-sent
model context. Restart the workspace to clear that context. Session summaries and
saved facts follow the same setting. No raw audio recording is added by this adapter.

Message requests, screen/camera model input, visual computer control, code tools and
file mutations require review of exact tool arguments. This is not an OS sandbox;
approved Python and tools run with the current Windows user's privileges. Main SARU
source edits continue through its existing Improve workflow. Plugin installation shows
the exact local Python source and binds approval to its hash; changes require review
again. Nothing is downloaded or executed simply because a README advertises it.

Phone access stays off until **Remote Control** is clicked in Advanced. It requires
HTTPS, a locally generated certificate, QR pairing and an owner-permitted LAN path.
SARU does not add firewall exceptions or fall back to HTTP. The phone must explicitly
trust the certificate. This is a browser dashboard, not full Android/iOS system control.
No account, remote listener, social message or post is activated by installing source.

## Supplied-source gaps and licenses

The upstream README advertises 26 plugin paths absent from the supplied plugin folder.
Five names have bundled action equivalents; 21 advertised plugin implementations were
not supplied. Advanced's status panel lists each gap. In particular, advertisements
for Gmail/calendar/WhatsApp automation do not mean those plugins are installed or
accounts connected. Existing SARU integrations remain available with their own setup.

See [component attribution](mark_suite/ATTRIBUTION.md), the original
[CC BY-NC 4.0 license](mark_suite/LICENSE), and the third-party asset licenses under
`mark_suite/THIRD_PARTY`. Mark's noncommercial terms apply to that component; they do
not grant a new license to unrelated SARU source or artwork. The inventory records
bundled file hashes and the single upstream upload-path adaptation.

Verification includes exact-bundle hash checks, encrypted read/write/corruption
preservation tests, duplicate-launch/microphone handoff tests, isolated Qt construction
and all 17 action registrations with SDK config construction. Provider self-tests use
mock services and synthetic settings. External accounts and local speech models still
need their own setup and acceptance checks.
