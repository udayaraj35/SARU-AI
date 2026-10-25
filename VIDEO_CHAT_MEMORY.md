# SARU 2.17 Video, chat and memory

Open **YouTube**, **YouTube Player**, or type **open youtube player**. Playback uses a
SARU-owned native Qt window, with an embedded YouTube player and a chat pane. It does
not launch an Edge/Chrome tab or app popup. Drag the divider or the window edges to
resize. Large/Small, minimize, F11/fullscreen and Escape/restore remain available.
The existing main dashboard and Advanced workspace keep their own layouts.

Paste a YouTube URL or enter a video title in the top input, then Play YouTube.
Search retrieves public result links and adds up to eight to the private media
library; **Next/Previous cycle the saved library**. A failed search asks for a direct
link rather than opening a browser. Search markup can change. Playback uses the
official YouTube IFrame API, requires Internet and honors video embed/region/account
restrictions. A restricted video displays a playback error in the screen. There is
no automatic external-browser fallback, DRM bypass or YouTube media download.

The bottom controls provide Play/Pause, Previous/Next, ±10 seconds, volume and
fullscreen. Local imports and MP3 clipping of owner-selected local files are retained.
The transport stays visible when the screen is small; optional favourites/import and
local clipping forms expand from their own detail controls.
Favourite YouTube entries are links, not offline files. A pending export still uses
SARU's existing local Save dialog.

## Text and voice

The side chat uses the same SARU chat/command route and configured provider as the
main app. It has no separate API key. Websites cannot invoke a Python chat bridge;
chat uses a private pipe between SARU and its child window. Main Live voice remains
responsible for microphone, wake gating and output. Its addressed transcript is
also shown in the video screen while open. Closing all of SARU closes this screen.
Closing just the screen leaves the main assistant running.

Examples, prefixed with SARU when spoken:
- `play youtube Nepali songs` or `youtube search Nepali songs`
- `play https://youtu.be/M7lc1UVf-VE`
- `pause video`, `resume video`, `next video`, `previous video`
- `video volume 50`, `video volume up`, `video volume down`, `mute video`
- `video forward`, `video back`, `video fullscreen`, `video small`, `video restore`

Playback/navigation requests use direct local command dispatch. Queued playback
requests are applied in order, including rapid next/volume/pause requests. Other
PC/file/account/source workflows retain their existing reviews and limitations.

The wake gate now accepts punctuation after SARU and the supported Nepali spellings.
It also accepts the explicit name returned as spelled-out SARU letters in Nepali.
ASR vocabulary hints include SARU; ordinary `Sorry` is not a wake phrase. Speech
recognition can still mishear a name, so speak it clearly or use text input.
When transcription arrives as a split wake token, its whole recognized utterance
is displayed once authorization is confirmed. `SARU`, `hello SARU`, or `SARU hello`
are addressed greetings; an otherwise silent completed greeting requests the
configured listening acknowledgement. Voice needs a valid Gemini Live model/key,
working microphone/speakers and Internet. Recognition is not speaker verification;
If a saved device index points to an output-only device as the microphone (or the
reverse), runtime uses the valid system default and emits an audio-warning event; existing
saved preferences are retained. Other audio-format/device failures remain visible.
unaddressed background speech is still excluded from conversation events. Nothing
here records all ambient audio or promises perfect speech recognition.

Text chat also recovers from a retired Gemini text model returning HTTP 404. It lists
models available to the same key and tries one verified stable numeric Flash model
once, then caches the working selection for 15 minutes. It does not change saved
settings or credentials, retry quota/auth failures, select a Pro/image/TTS model or
claim an answer when none arrived. The actual replacement appears in SARU status.
Network timeouts remain visible and are not automatically retried.

## Visual memory

Use **Saved memory** or Settings → Memory → View notes. The map uses actual local
record counts for conversations, notes, task results, Office work and exported
files. Click a category to filter the timestamped history, or the centre for all.
Search, notes and export are retained. The display shows the actual database path,
size and recording ON/OFF state. It refreshes when saved data changes; the pulsing
map is a visualization, not evidence of an AI thinking or a job running.

The owner-supplied Zoey reel inspired the visual overview. Its public portion and
description were visible, but Facebook gated further viewing behind login. This is
not an exact copy of an unseen memory screen and does not add the reel's advertised
900 integrations. Existing private data, credentials, profiles and settings remain
local. Disabling automatic memory retains existing records and stops automatic
recording/lookup according to the existing memory rules.
