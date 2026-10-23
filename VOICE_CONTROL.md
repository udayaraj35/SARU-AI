# SARU 2.9 voice and text controls

Explicit app/site opening, normal navigation, buttons and ordinary SARU settings now run directly without generic OK/Cancel. Sensitive workflows retain their own specific review, such as sending camera frames or applying a source diff. "cancel" cancels. Approval applies once to the current proposal and expires after two minutes. A replacement proposal invalidates the previous one.

Examples: theme blue; full screen; open settings; use new photo; photo size 110; text size 120; open Notepad; list windows; choose window 1; screen task write Hello in Notepad.

App launches run in the background. SARU reports opened only after finding a matching visible window. Ambiguous app names return numbered choices: select app 1.

Screen tasks require a configured Gemini vision key/model. Screen sharing and each exact proposed input require separate approval. Changed or stale proposals are refused. Protected Windows prompts and account permissions remain controlled by Windows and the respective service.

The default dashboard and companion now load saru_avatar_neon.png. Use original photo restores the original portrait. Selecting a custom portrait preserves that choice.

These controls cover implemented actions. Arbitrary self-editing and universal control of every app are not verified capabilities.

## Windows power
Say shutdown pc / pc off gara, lock pc / pc luck gara, or sleep pc / sleep mode. Approve the visible proposal with OK or hunxa within 30 seconds. Shutdown has a further 30-second delay; cancel shutdown requests Windows cancellation. No forced application termination is added. An enabled owner security PIN still applies. Actual power transitions are not run by the test suite.

Native sleep and lock use Microsoft Windows APIs: https://learn.microsoft.com/en-us/windows/win32/api/powrprof/nf-powrprof-setsuspendstate and https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-lockworkstation

## Owner edit verification
Use unlock saru changes to open a masked local code field. Verification unlocks the reviewed Improve SARU workflow for ten minutes; authorization is checked again at apply time. The edit code is stored as a salted PBKDF2 hash and is separate from the existing security PIN. Five failures cause a one-minute cooldown. Entering the configured code directly as a text message is intercepted before normal chat/memory routing; speaking any secret in cloud voice may send it to the voice provider, so use the masked local field.

Only explicitly requested edits to selected editable SARU source files are staged. Review the exact diff and approve each apply. Protected recovery/security/update files, external files, keys and memory are excluded. Syntax checks do not establish functional correctness. Restart and test after applying; rollback is available. This is not unrestricted self-rewriting or guaranteed support for every requested capability.

## SARU app controls
Say saru controls for the current command list. Settings controls include floating size 48–240, floating text size 10–22, floating opacity 35–100, speech speed 80–300, show/hide floating saru, enable/disable animations, romantic/friendly/professional mode, speak/silent replies, enable/disable auto listening and remember conversations / stop remembering conversations. Commands save bounded values, not arbitrary settings dictionaries. Changing companion style or memory while Live Voice is active stops that session; start voice applies the updated preference.

After owner edit verification: saru update request <specific change>; saru update files dashboard_ui.py, settings_ui.py; generate saru update. Approve disclosure of the selected source, inspect the exact diff, then apply saru update and approve that exact change. rollback saru update restores the loaded proposal only after owner review. Changed requests/file selections/proposal identities invalidate pending reviews. All source edits remain restricted to editable SARU files; missing capabilities are not fabricated.

## Explicit destinations and unattended messages
open WhatsApp web opens SARU Browser. open WhatsApp in PC / open WhatsApp desktop requests the installed Windows app. open Google Chrome explicitly launches Chrome; open browser uses SARU Browser. Native launch still reports success only with matching window evidence.

fill password locally opens a masked one-time prompt only when an HTTPS site password field is focused in SARU Browser. Passwords are not logged to SARU chat, stored in its database, copied to clipboard, or auto-submitted by this helper. Subsequent fills ask again; website session cookies may keep you logged in. Python/website memory cannot be promised physically zeroed. Never speak passwords to cloud voice. Marked password/OTP/API-key text is excluded from SARU text chat and memory on a best-effort basis; unlabelled secrets cannot be detected reliably.

With configured WhatsApp Business credentials: schedule whatsapp in 10 minutes to +9779800000000: Hello. This exact scheduling command authorizes one future attempt; no additional generic prompt. show scheduled messages / cancel scheduled message 1 inspect and cancel pending work. Queue payloads are Windows-user encrypted. Account/token changes block sending. Interrupted/unknown results are never retried automatically. Jobs over ten minutes late expire. SARU must be running and PC awake. Personal WhatsApp Web drafts are not claimed to be reliable unattended sends. Delivery requires Meta confirmation beyond request acceptance.
