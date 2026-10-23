# SARU camera, reminders and voice profiles

Commands:
- open camera / stop camera
- what am i doing / ma k gardai xu
- camera ask Where is my cup?
- remind me in 10 minutes to call family
- 5 minute paxi pani piu samjhau
- alarm 07:30: Wake up
- show reminders / aaja ko baki kam
- complete reminder 1 / cancel reminder 1
- save my voice as Udaya / compare my voice / voice profiles

Camera opens only on an explicit owner request. Local preview is not archived. Analyze freezes a single frame; owner approval is required to send that image/question to configured Google Gemini. Stop closes the device. Objects outside the frame and activity outside that moment are unknown. This does not identify people or continuously observe the room.

Reminders persist in AppData/SARU_AI/reminders.sqlite. Exact clock times use Europe/Sofia, with the next occurrence shown before approval. Relative durations freeze at proposal time. Alerts use a visible notification, system sound and optional local speech. SARU must be running and PC awake. No Windows wake timer/background service is installed; overdue reminders appear on reopen. Notified tasks remain in the remaining-task list until completed/cancelled.

Voice enrollment explicitly records 12 seconds, stops active Live Voice first, and saves the sample plus speaker embedding protected with Windows-user DPAPI in AppData/SARU_AI/voice_profiles. Enroll only consenting speakers. Stop cancels recording; profiles can be deleted in the profile window. Comparisons are local, on demand, and uncertain. This is not automatic continuous speaker identification or an authentication factor. Unknown/ambiguous input does not authorize actions. No voice cloning is implemented. Restart voice after enrollment if desired.

Camera needs OpenCV and vision needs a configured Gemini key/model. Local voice comparison uses Resemblyzer/CPU PyTorch. Install prebuilt webrtcvad-wheels rather than compiling webrtcvad; install Resemblyzer with --no-deps after installing torch, librosa, scipy, numpy and typing. The provided setup_voice_profiles.py performs that setup. Device and real-person accuracy have not been established by mocked tests.

Sources: https://github.com/resemble-ai/Resemblyzer and https://docs.opencv.org/3.0-last-rst/modules/highgui/doc/reading_and_writing_images_and_video.html
