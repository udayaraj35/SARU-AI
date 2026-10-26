# SARU AI 2.20.1

Windows personal assistant with a native neon dashboard, text/live voice, local PC tools, SARU Office and optional integrations. This repository contains the Windows source; an Android app has not yet been implemented.

2.20.1 routes everyday WhatsApp message and YouTube playback requests to the existing task executors, accepts media follow-ups after waking once, and supports explicit input in the currently selected PC Control app. WhatsApp drafts use the visible social session and final reviewed Send; QR/login and exact recipients are still required. No production-account delivery is certified. See [commands and limits](TASK_SHORTCUTS.md).

2.20.0 adds the owner's video-inspired **Holographic workspace**: a locally rendered purple/blue particle sphere and wave floor, actual voice state and measured PC readings, plus working Chat / Controls / Configure buttons. Click the sphere for Saved Memory. Settings → Appearance can restore the Portrait workspace or enable Reduced motion. Existing sidebar tools, right chat, bottom composer, country clock and Owner-profile internet status are retained. The video's narrated analytics/email claims are not displayed as fabricated activity. See [workspace behavior and validation](HOLOGRAPHIC_WORKSPACE.md).

2.19.0 changes the requested default to **wake once, then converse**. Say SARU to hear “हजुर Boss, म के सेवा गरूँ?”, then give questions or supported commands without repeating the name. After 60 seconds idle or Stop listening, SARU is required again. Strict per-utterance activation remains an option in Settings → Voice. Typed notifications never activate a microphone conversation; this feature is activation rather than speaker authentication. The right chat drawer and country-clock layout are preserved. See [voice conversation behavior and validation](VOICE_CONVERSATION.md).

2.18.4 moves the measured Online/Offline indicator below Owner profile and places the selected clock/date at the top right. Click the clock, or open Settings → Appearance → Clock / Country & Timezone, to choose from the offline IANA country list and that country's city/timezones. This selector appears first in Appearance so it is visible immediately. Countries spanning multiple timezones require a city selection. Saved clock preferences survive restarts and observe the selected timezone's DST rules. The Windows system clock, separate Nepali calendar and configured weather city are preserved.

2.18.2 fixed an observed full-question wake-name transcription failure: Gemini transcribed a synthetic “SARU, what is two plus three?” as uppercase `SAU, what is 2 + 3?`, which the local wake gate discarded. The gate recognizes that narrowly punctuated uppercase ASR form with a nonempty request. Ordinary `sau`, unpunctuated `SAU`, `Sorry`, `Sarah` and embedded names do not activate wake mode. A real provider test returned the correct Nepali answer with audio. That release retained strict per-utterance activation, which is now optional in Voice settings.

2.18.1 places conversation messages in a right-side drawer while retaining the bottom message composer. Voice/text conversation opens the drawer automatically; after a completed reply, 30 seconds of inactivity hides it without deleting history. Reading with the pointer over the drawer, an in-progress reply or unsent text keeps it open. The header × hides it immediately; the Chat button, `open chat` / `chat open gara` / `च्याट खोल` reopens it, and `close chat` / `chat banda gara` hides it. A manually hidden assistant turn stays hidden until new owner speech or explicit opening.

2.18.0 adds local multilingual FAISS memory with SQLite facts, streaming reviewed shell/file tools, persistent Playwright social sessions, pinned executable Git skills with separate environments, additional encrypted provider configurations and signed source-update staging on restart. Existing dashboard styling/layout is retained. Social DOM adapters require local login and unique visible controls; no production-account delivery is certified. Executable skill repositories need a reviewed `saru_skill.json` contract; arbitrary GitHub references are not automatically executable. See [backend architecture, setup, commands and limits](BACKEND_ENGINES.md). On a new PC, after installing requirements, run `python backend_setup.py --memory --browser --receipt` once. Signing keys, account sessions and memories are never included here. Frozen builds use a separately prepared installer.

2.17.0 adds SARU's native **Video & Chat** window: embedded YouTube/local media, a resizable chat pane, queued play/pause/next/previous/volume controls, fullscreen and direct text/voice playback commands. YouTube actions no longer open a browser tab. Saved Memory now has a themed visual map built from actual record counts, filtered timeline, live refresh, recording state and database size/path. Voice fixes include full split-wake transcripts, punctuation/spelled-name recognition, greeting acknowledgement and runtime fallback when an obsolete device index selects a speaker as the microphone. See [video, chat and memory setup/limits](VIDEO_CHAT_MEMORY.md). External account, device, speech recognition and YouTube embed restrictions still apply.

2.16.0 integrates the owner-supplied Mark LVI source as **Advanced workspace** in Apps & Tools and Settings → Tools. It provides a separate 3D avatar/viseme interface, 17 discovered action tools, undo, provider configuration and opt-in HTTPS phone dashboard while retaining the main SARU interface. Main voice pauses while Advanced owns the microphone; Ctrl+Space is its default push-to-talk. Advanced dependencies and browser engines install separately. Config/facts use Windows DPAPI; journal recording follows SARU's memory switch. External providers/accounts/local models require setup. The upstream README advertises absent plugins; they are explicitly listed as unavailable rather than represented as installed. See [setup, capabilities and limits](ADVANCED_WORKSPACE.md) and [attribution](mark_suite/ATTRIBUTION.md). Mark's component retains CC BY-NC 4.0 noncommercial terms.

2.15.0 adds a private searchable memory journal for conversations, notes, actual task results, Office job snapshots and exported file paths. Open Settings → Memory → View notes or Apps & Tools → Saved memory. Text chat gets bounded relevant memory; Live voice can request a read-only topic lookup during the current addressed conversation. The sidebar now spans the window independently of bottom chat, fitting its buttons to available height and supporting local wheel scrolling when small. See [memory and sidebar behavior](MEMORY_AND_SIDEBAR.md) for recording controls, migration, privacy and limitations. The prior voice reply fixes are retained.

Text-model retirement recovery now handles a saved Gemini model returning 404 by discovering a stable Flash replacement for the same key and retrying once. It preserves saved settings, shows the working model in status and never retries quota/auth failures. Three focused recovery checks passed; a synthetic request to `gemini-3.8-flash` returned text successfully. Network timeouts remain visible.

## Run on Windows

Use Python 3.11+ on Windows 10/11. Run `install_and_run.bat` for the guided installer, or create a virtual environment, install `requirements.txt`, and run `launch_saru.py`. Configure your own provider/API keys in Settings; they are not included in this repository.

## Current interface

The 2.12.0 dashboard keeps the dark/pink reference design: large SARU portrait, central actions, measured PC status, Quick Tools and recent tasks on the right, and chat at the bottom. Settings stays near the bottom of navigation. Apps & Tools exposes existing actions and integrations. All four themes preserve the layout. Device & AI controls reveals the inline sliders/provider settings.

## Capabilities and setup

- Text and live voice, including the configured SARU wake prefix. A wake word does not authenticate the speaker. Connected voice uses the configured cloud provider.
- Real app launching and supported Windows device/input tools; this does not bypass UAC or secure desktop restrictions.
- Local memory, owner/creator profiles, reminders, camera/screen assistance and document/media workflows with their existing setup requirements.
- SARU Office, task submissions and output exports.
- Optional WhatsApp CRM requires a configured Supabase project and Meta/WhatsApp Business credentials. It is not an already-connected personal WhatsApp inbox.
- Existing website/social integrations have their own authorization and review requirements. No production messaging or posting is implied by the dashboard.

## Privacy and assets

Runtime settings, encrypted API keys, memory databases, logs, browser sessions, work files and installed dependencies are excluded. Windows user data remains under `%APPDATA%/SARU_AI`; the repository does not include that directory. Bundled developer/profile artwork and brand assets are retained for the application. See `BRAND_ASSETS.md` for asset notes and relevant third-party terms.

`wacrm_source.zip` contains reviewed public WACRM source pinned to `34bce1a8abf56281505d90bac165123b6ab7d51a`, including its upstream MIT license. Keep third-party notices. No new open-source license is granted to SARU's own code by this repository setup.

## Verification

2.17 passed 245 regression tests, full isolated main GUI smoke, native Qt video/chat rendering/resize/fullscreen checks, ordered player JavaScript tests and a real embedded official YouTube sample playback/pause/volume test. Playback controls were also checked in normal/compact viewports, and the installed video-side chat executed a real local calculation. Synthetic Saa-roo greeting audio through the configured Live service produced both transcript and response audio, with no microphone recording or personal memory. An English TTS rendition misrecognized as “Sorry” remained blocked; vocabulary hints do not guarantee perfect ASR.

The 2.16 integration passed 99 upstream provider checks with synthetic settings/mocks, 11 Advanced/installer tests, 54 existing memory/voice/own-app regressions, full isolated dashboard smoke and Qt/config construction with all 17 actions. Downloaded Chromium and Firefox each opened an isolated blank page. These checks do not connect external accounts or establish that every automation workflow works on every PC.

The 2.14.0 desktop update passed 218 regression tests, isolated GUI smoke at three sizes/all four themes, and the bundled Windows setup self-test. These checks do not establish that every external account, physical device or social publishing workflow is configured or acceptance-tested.

```powershell
python -m unittest discover -v
python smoke_gui.py
```

`smoke_gui.py` uses temporary data and disables automatic listening. Some tests require Windows GUI support and local loopback access.

## Developer

Udaya Raj Khanal. The application's editable creator profile contains the supplied contact/social details. See `profiles.py`.

Older specification/audit documents describe development history and requested features; their presence does not mean every requested feature is implemented. Use the current code and validated status above.

## Own-app commands

`open saru`, `hide saru`, `close settings`, `restart saru`, `close saru`. Fully closing SARU also stops voice. Self-improvement requests suggest related existing source files; generation requires source-sharing review and applying an exact diff retains owner verification, backup and rollback. See [OWN_APP_CONTROL.md](OWN_APP_CONTROL.md). Candidate edits are syntax-checked, not automatically functionally tested or unrestricted self-rewriting.

## Voice and connectivity fix

2.14.0 preserves audio received before wake transcription, reports local command results through the selected Live voice and keeps provider errors visible. Warm-romantic conversation supports natural Nepali delivery. Green Online/red Offline use cached Internet reachability checks rather than adapter link state. MYRA voice equivalence is not verified; no proprietary engine or credentials are copied. See [VOICE_REPLY_CONNECTIVITY.md](VOICE_REPLY_CONNECTIVITY.md). A synthetic real-account Gemini Live test returned Aoede audio without microphone recording or personal memory.
