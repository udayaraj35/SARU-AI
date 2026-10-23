# SARU 2.10.1: direct owner PC input

Exit SARU fully and reopen after updating. Settings, keys, profiles and memory are preserved.

Say or type:

1. `use Notepad: write Hello SARU` — finds/opens the installed app, attaches its real window, and writes once into its focused field. Multiple app/window matches need an exact choice.
2. `pc type नमस्ते` — types one line into the selected app's focused field, without clicking another point or touching the clipboard.
3. `pc press ctrl+a`, `pc press ctrl+c`, `pc press ctrl+v`, `pc press ctrl+s`, `pc press Enter` — supported shortcuts, including submissions when you explicitly request Enter.
4. `pc click 100, 200`, `pc double click 100, 200`, `pc right click 100, 200` — primary-screen pixel coordinates. The point must belong to the selected app. Do not guess coordinates; inspect the actual PC Control capture.
5. `pc scroll down 3` / `pc scroll up 3` — pointer must be over the selected app.
6. `pc stop` — cancels queued input/capture/planning callbacks. Already completed inputs are not undone. Move pointer to a screen corner to trigger the input fail-safe.

Exact local input commands run without another generic OK/Cancel prompt. Commands are routed only from the user's text or completed voice transcript, never the assistant's generated reply. A queued status is not a completion claim: the later status reports actual execution or failure. A fresh capture follows each successful input.

This is not universal autonomous computer access. Screen-based AI planning still needs a configured Gemini vision key/model and screen-sharing/action review. Administrator apps, Windows UAC, the lock screen and secure desktop remain governed by Windows. Ordinary app opening is separate from device/account authorization. Cloud account logins and social posting need their appropriate account setup. Passwords should use local masked browser entry, never ordinary voice/chat typing. Voice recognition and target matching can be imperfect; inspect results before repeating a command.

Validation uses mocked input/accounts; no real messages, password entry, shutdown or privileged Windows operations are performed by the regression tests.
