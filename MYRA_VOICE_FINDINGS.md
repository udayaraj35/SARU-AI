# Installed MYRA inspection and SARU voice update — 2026-10-20

## Observed on this PC
- Distribution: myra-ai-assistant 0.3.3, installed in the Python 3.11 site-packages directory.
- CLI entry point: myra.cli:main; launcher in Python311/Scripts/myra.exe.
- Main modules are compiled CPython 3.11 Windows AMD64 .pyd files. This is not a reusable published Python voice-engine interface.
- Existing .aria/config.json language is ne. Only setting names and that language value were inspected for reporting. API-key values, user name and private session memory were not printed, imported, copied or modified.
- The bounded log scan found no voice/session event tokens in the selected tail. This does not establish how MYRA behaves during an actual conversation.
- aria.pyd SHA256: 8cfa0219c85fdf040ed0120184d5b4a0ae96d78c6b6d51283a5cadfb53422975.
- myra_ui.pyd SHA256: 26cf4c3941795f3e7a8d687c6fd864c38dfa03dfb45128ddd0bf2c2da2adc643.
- REA successfully identified aria.pyd as PE x86_64. Its native string analysis was unavailable because no Ghidra/IDA/Hopper provider is configured. Session closed. No decompilation or proprietary engine copying was performed.
- A separate shell byte-string scan found short Aoede/16000 fragments; these are weak hints, not proof of runtime behavior or the complete audio architecture.
- Bundled MYRA install documentation describes Gemini Live voice. That documentation is a product claim, not an observed conversation on this PC.

## SARU 1.1.0 changes
New independent Gemini Live adapter based on Google's documented SDK, not MYRA internals:
- Continuous streaming conversation while the user explicitly starts the session.
- Own SARU Gemini key, independently selectable Live model and cloud voice.
- 16 kHz mono PCM16 microphone input, 24 kHz PCM16 speaker output.
- Bounded input/playback buffers; asynchronous send/receive; multiple conversation turns.
- Input/output transcriptions on the voice page only; no automatic transcript persistence.
- Real PCM audio-level meter, Start, Stop and mic mute.
- Speaker mode suppresses mic transmission while playback is active; headphones mode allows overlapping input and server interruption handling. This is not acoustic echo cancellation.
- Navigating away stops the voice session. Classic push-to-talk remains available and is prevented from overlapping with Live Voice.
- This Live Voice adapter has no computer/account tools. Use PC Commands for actual actions; the voice model is explicitly told not to claim it performed them.
- No wake-word detection, speaker authentication, video or automatic reconnect is added in this release.

## Sources
- https://ai.google.dev/gemini-api/docs/live-api/get-started-sdk
- https://ai.google.dev/gemini-api/docs/live-api/capabilities
The checked official guide uses gemini-3.8-live. Model availability/quota varies by key; keep the separate Live model field configurable.

## Verification and limits
- 28 automated tests pass, including synthetic two-turn audio/transcript and cancellation/cleanup tests.
- Google GenAI SDK 2.31.0 installed into project-local .voice-sdk for validation only. Typed LiveConnectConfig and async close interface validated without a provider request. The updated installer installs this dependency into SARU's isolated venv; MYRA's global environment was not changed.
- Real Windows GUI smoke passes including Live Voice navigation, 8 Settings tabs, save/validation and 3 sizes.
- PC default devices: Realtek microphone array and speakers/headphones. Input 16 kHz/output 24 kHz format validation passes. No recording, playback, MYRA live session or paid API request was made.
- Actual speech quality, Nepali recognition/pronunciation, latency, VAD and interruption behavior remain to be tested with the owner's authorized Gemini configuration and real audio.

## Use
1. Close old SARU and run install_and_run.bat to add google-genai in SARU's venv.
2. Settings > AI & API: save your own Gemini key (you can retain a different text-chat provider).
3. Settings > Voice: select Live model, voice name, microphone/output device and headphones mode; Save.
4. Dashboard > Live voice conversation > Start conversation. Audio is sent to Google only while started. Stop or leave the page to close the session.
5. Use classic push-to-talk if the Live model/account is unavailable. No MYRA key is imported automatically.
