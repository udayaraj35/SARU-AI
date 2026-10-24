# SARU AI 2.16.0

Windows personal assistant with a native neon dashboard, text/live voice, local PC tools, SARU Office and optional integrations. This repository contains the Windows source; an Android app has not yet been implemented.

2.16.0 integrates the owner-supplied Mark LVI source as **Advanced workspace** in Apps & Tools and Settings → Tools. It provides a separate 3D avatar/viseme interface, 17 discovered action tools, undo, provider configuration and opt-in HTTPS phone dashboard while retaining the main SARU interface. Main voice pauses while Advanced owns the microphone; Ctrl+Space is its default push-to-talk. Advanced dependencies and browser engines install separately. Config/facts use Windows DPAPI; journal recording follows SARU's memory switch. External providers/accounts/local models require setup. The upstream README advertises absent plugins; they are explicitly listed as unavailable rather than represented as installed. See [setup, capabilities and limits](ADVANCED_WORKSPACE.md) and [attribution](mark_suite/ATTRIBUTION.md). Mark's component retains CC BY-NC 4.0 noncommercial terms.

2.15.0 adds a private searchable memory journal for conversations, notes, actual task results, Office job snapshots and exported file paths. Open Settings → Memory → View notes or Apps & Tools → Saved memory. Text chat gets bounded relevant memory; Live voice can request a read-only topic lookup during the current addressed conversation. The sidebar now spans the window independently of bottom chat, fitting its buttons to available height and supporting local wheel scrolling when small. See [memory and sidebar behavior](MEMORY_AND_SIDEBAR.md) for recording controls, migration, privacy and limitations. The prior voice reply fixes are retained.

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
