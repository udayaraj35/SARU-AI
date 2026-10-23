# SARU 2.3 desktop controls

Single-click the floating portrait to toggle quick controls. SARU waits for the Windows double-click interval so a double-click opens only the main dashboard. Dragging still moves and saves the portrait position.

Quick controls provide voice start/stop, microphone mute, manual screen view/reviewed screenshot sharing, Settings, and volume/brightness sliders. The sliders read actual Windows device values asynchronously and remain disabled when an endpoint is unavailable. Native device writes use the existing isolated latest-value worker. The screen workspace opens independently of the main dashboard; capture is manual and sending an image to Gemini still requires review. This is screenshot sharing, not a continuous screen broadcast.

The panel follows the selected theme, uses gradient buttons and raised edges, and pulses its border unless reduced motion is enabled. Readonly/disabled ttk fields, dropdown menus and legacy list selection now have explicit contrasting colors.

Command routing accepts polite English/Nepali wrappers and additional supported paraphrases, such as `could you open Chrome please`, `Chrome खोलिदेऊ`, `आवाज ४० प्रतिशत बनाइदेऊ`, and `show my screen`. Notes and draft bodies retain their content. Unknown conversation still goes to the configured AI; these changes do not add arbitrary command execution. Code change requests open the existing reviewed improvement workflow rather than applying source changes silently.

Validation: regression suite plus isolated GUI smoke checks cover click timing, drag behavior, paraphrases, panel creation, independent screen workspace, all four themes and readonly text contrast. Live microphone/cloud connections and publication are not exercised by those checks.
