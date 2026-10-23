# SARU 1.7.0 PC Control

Open PC Control from the dashboard, or type `pc control` in chat.

1. Choose app window > select an app > Focus selected app and capture. Alternatively open the target app, return to SARU and use Capture screen.
2. Select the target in the screenshot.
3. Use Click selected point or choose type, double click, right click, scroll or shortcut.
4. For type, enter one line (up to 2000 characters). Nepali and emoji are sent through Windows Unicode input without replacing the clipboard. For scroll use -10 to 10; positive scrolls up. For shortcut choose the predefined combination; it acts on the already focused control in the captured app.
5. Review the exact action, then run it. Capture again to inspect the result.

Input requires a screenshot newer than 30 seconds, the same foreground window, matching display scaling and an unchanged local target patch. Moving the mouse to a screen corner triggers PyAutoGUI fail-safe. Input is never retried automatically. Text does not include newline/control characters; Enter is a separate reviewed action because it may send or submit. Choosing a window does not run commands or close applications. Window list excludes SARU's own process.

Screen capture/input currently supports the primary monitor. Gemini screen reading uses the existing separately approved cloud screenshot workflow and requires a configured Gemini model/key. No local OCR engine, continuous screen watcher, autonomous action-planning loop, drag/drop or arbitrary shell execution is added. Elevated apps/UAC, secure desktop, games, remote sessions and controls that do not accept Unicode keyboard events may reject input. Check results after each action; this is expanded assisted PC control, not complete universal autonomy.

Validation: 16 related unit tests passed, including stale/changed target rejection, window focus changes, Unicode dispatch, payload bounds, shortcuts, scroll and click variants. Main dashboard smoke and extended PC Control/window picker GUI checks passed. Automated tests did not send input to the user's real apps. Physical keyboard/mouse injection into third-party apps remains unverified.
