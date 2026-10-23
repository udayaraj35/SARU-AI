# SARU 2.4: Voice playback and personal media

Audio responses can arrive faster than a speaker plays them. The old eight-second queue raised an exception and disconnected. The queue now rejects an append before exceeding its bound, and the async receiver feeds it in small chunks while the device drains it. Samples remain ordered and are not silently discarded. A genuinely stalled device still reports a specific device error. PortAudio timing flags no longer terminate an otherwise healthy session. The regression tests simulate a burst, verify every sample, and check stop and stalled-device behavior. A long real microphone/cloud conversation still depends on the selected hardware, network and Gemini account.

Completed explicit voice requests can ask for code improvements without an exact SARU prefix. They open the existing reviewed improvement workflow. Concrete missing-feature requests offer to prepare a proposal. Generation still asks before sending selected source, and applying requires the exact source diff, backups and approval. The assistant's conversational instructions explain these steps constructively rather than claiming an unimplemented action happened.

Click **YouTube Player** in the sidebar or say **SARU, open youtube player**. The player opens in an Edge/Chrome app window, with normal minimize/maximize buttons. It follows the theme selected when it opens and provides saved favourites, play/pause, previous/next, ten-second seeking, volume and fullscreen. YouTube's official embedded player needs internet and can reject embedding for restricted videos. Saving a YouTube favourite stores its link, not an offline download or extracted audio.

Use **Import local file** to choose an owned/local media file in SARU's dialog, then refresh the library. A copy is stored under the SARU data directory's `media` folder so the original can move independently. Supported imports: MP4, WebM, MP3, WAV, OGG, M4A, MOV, at most 1 GiB. Playback codec support depends on the browser. Select a local file, enter start/end seconds, and choose **Save MP3 clip** to create a separate MP3 without changing the source. MP3 conversion uses the bundled FFmpeg runtime, not YouTube downloads.

Examples:

- `save youtube https://www.youtube.com/watch?v=VIDEO_ID as My favourite`
- `play saved video My favourite`
- `pause video`, `next video`, `previous video`, `video volume 60`
- `आफ्नो कोड सुधार नयाँ theme थप`

Voice commands still show a review before requesting actions. Browser autoplay policies may require an initial click on Play. The media server binds only to 127.0.0.1 with a random session path, validates Host and write tokens, and serves only media registered in the library. It does not expose an arbitrary filesystem browser or shell.

Protocol references: [Gemini Live audio](https://ai.google.dev/gemini-api/docs/live-api/capabilities), [YouTube IFrame Player API](https://developers.google.com/youtube/iframe_api_reference).
