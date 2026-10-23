# PC app control · 2.7.1

Routing fix in 2.7.2: `app khola`, `एप खोल्नुहोस्`, `Chrome खोलिदिनुस्`, and similar explicit requests go to the local launcher/app picker before general AI chat. A missing app name opens the picker. Explicit ordinary voice app launches no longer wait for an extra command confirmation; sensitive workflows keep their reviews. Recognized live-voice commands suppress the cloud model's unrelated reply/audio and report the local command result. Restart SARU fully after updating so the running voice session loads the new routing and prompt.

From PC Control choose Open installed app, select an entry and choose Use app / PC Control. SARU launches it, finds its visible window and captures the primary screen locally. If multiple matching windows are open, choose the exact one. No unrelated window is selected silently. Missing portable applications can be added by selecting their executable.

Voice/text examples:

- `use Notepad: write Hello SARU`
- `open Calculator and click 7`
- `Notepad kholera mero naam lekhnu`

The app name and task are kept separate. These commands open the app-control workspace with the goal; they do not immediately execute a guessed click. Select a point in the real screen for click, double click, right click, Unicode typing, scroll or a supported shortcut. Review the input, then SARU activates the same target window, checks screen freshness/target changes and performs one action. It captures the result automatically before the next step.

Gemini can propose the next action using an explicitly approved screenshot and task. Configure a Gemini vision model/key first. The proposal includes the exact action and target for review. Recent performed input types are included as context; effects must be verified from the new screenshot. Inputs are never arbitrary shell code.

Windows Store applications use IApplicationActivationManager, following Microsoft's documented activation interface. Desktop executables and Start Menu shortcuts retain their normal launch methods. No administrator elevation or permission bypass is performed. If Windows blocks activation/input, open the app normally and choose its running window. Protected desktops, permission dialogs and apps requiring different integrity permissions may remain inaccessible.

References: https://learn.microsoft.com/en-us/windows/win32/api/shobjidl_core/nn-shobjidl_core-iapplicationactivationmanager and Microsoft's WindowsAppSDK MddBootstrap.cpp (CLSCTX_INPROC_SERVER).

Validation: command parsing, app/window matching, ambiguity, native activation wiring, stale/focus guards, Unicode input and automatic recapture covered by local tests. GUI navigation is checked separately. Live Calculator end-to-end input testing was blocked by local activation access restrictions; the request to run that test outside the sandbox was rejected by automatic approval review. Live Gemini desktop planning was not tested.
