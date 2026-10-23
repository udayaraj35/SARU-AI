# SARU v17.0.1 project audit — 2026-10-20

## Fixed
- Chat read SQLite history and notes from a background thread, violating SQLite thread affinity. Capture memory and provider settings on the UI thread before starting the request.
- Deferred exception callbacks referenced cleared Python exception variables. Capture values in voice, microphone, model lookup and updater error callbacks.
- Installer omitted MYRA_OFFICIAL_GUIDES. Copy the bundled directory during installation.
- Installer read Tk checkbox variables in its worker. Capture checkbox choices before starting it.
- Initialize Windows COM in the shortcut worker.
- Avoid writing chat responses into a closed chat widget.
- Save settings through a temporary file and atomic replacement.
- Deep-copy default settings so nested key/model dictionaries are not shared with defaults.
- Honor saved microphone device selection.
- Recognize punctuation in hello/hey SARU greetings.
- Correct stale updater version from 12.0.0 to 17.0.1.
- Reject release asset filenames containing path separators or drive prefixes.

## Verified
- AST syntax validation: app.py, installer.py, update_manager.py.
- Mocked provider request executed on a real background thread with a real SQLite memory database; assistant reply successfully saved on UI callback.
- AST check confirms deferred exception callbacks bind their exception values.

## Remaining product limitations / unverified behavior
- GUI is a static image with fixed hotspots. Alternate backgrounds can misalign controls; image labels are not live telemetry.
- Actual minimize/maximize/close, floating assistant, installer upgrade and shortcut behavior still require desktop testing.
- API requests need a valid configured provider key and network. No live paid API request was made.
- Audio hardware, recognition and installed voices require a local device test.
- Social workflows create drafts/open sites; authenticated publishing is not implemented.
- Voice mode is push-to-talk, not continuous wake-word listening.
- MYRA guides are documentation; including them does not install or reproduce MYRA's engine.
- API keys remain local plaintext settings; Windows account access protects those files.
- Updater checksum checks corruption, not publisher identity. No update was downloaded or executed.

## Retrieved conversation context
Source: ChatGPT conversation "MYRA Install Guide".
Available user requests: move SARU v17 into Codex, remove duplicate window buttons, investigate and fix other problems.
The returned assistant messages contained content-reference markers rather than answer text; older detailed specifications and attached image contents were unavailable. Therefore a complete historical specification cannot be reconstructed from this tool response.
A separate "Banau installable AI agent app" conversation describes MAYA in D:\My Project\MayaFlow AI, a different codebase. Do not merge that source or assume its features exist in SARU.

## Next verification
Run install_and_run.bat on Windows, then test chat with a valid API key, close a chat while a request is pending, test a microphone error, inspect MYRA guides after installation, and exercise native window controls and floating orb. Back up AppData\SARU_AI before installing over an existing version.

## Personal assistant commands added
Main chat and voice now use the same command router. Commands support English plus common Roman Nepali/Devanagari phrases. Added YouTube search, calculator, volume/brightness, notes retrieval, app launch and text/code summarization. Chat messages that are not commands still go to the configured provider.

Examples: youtube kholnu; whatsapp खोल्नु; youtube ma Nepali songs khojnu; volume 50; brightness 70; calculate (12+8)*5; save note Buy milk; show notes; summarize file.

File summaries require confirmation before sending selected content to the configured provider. Supported text/code files are limited to 100 KB. PDF, Word, image/video generation, arbitrary website interaction and authenticated social publishing still require additional integrations. This build does not provide universal autonomous computer control.

Verification: python -m unittest test_assistant -v. Five test groups cover multilingual parsing, conversational false positives, arithmetic, syntax, and action execution with browser/device adapters mocked. Live GUI, account login, API requests and hardware effects have not been verified by these tests.
