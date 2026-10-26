# App tasks from voice and text — 2.20.1

An app launch is separate from an app task. SARU now routes explicit everyday WhatsApp and YouTube tasks to the existing executors, instead of treating the entire sentence as an application name or ordinary chat.

Examples after waking SARU:

- `YouTube ma Nepali folk music bajau`
- `युट्युबमा नेपाली गीत बजाऊ`
- `play Nepali folk music on YouTube`
- `send WhatsApp message to Test Contact: Hello`
- `WhatsApp ma Test Contact lai Hello message pathau`
- `WhatsApp ma Test Contact lai: Hello`
- `use Notepad: write Hello SARU`, then `current app type More text` or `selected app press ctrl+s`

YouTube requests use the embedded player and real public search. Media follow-up requests no longer depend on an English verb or repeating SARU; the existing upstream wake/conversation gate still applies.

WhatsApp uses SARU's existing visible Playwright social session, exact contact/phone lookup, draft preparation and reviewed final Send. The older numeric `whatsapp to +countrycodeNUMBER: text` path also uses this executor unless a WhatsApp Business account is configured. Login/QR must be completed in that social session once; the separate embedded Qt browser's login is not shared. A duplicate or unloaded contact is reported rather than guessed. No message is sent merely by parsing the command; the final reviewed action is submitted once and delivery is not claimed from a click alone.

Selected-app input uses the existing foreground/window guards. It cannot type into an arbitrary unselected app. Other complex application workflows still depend on the app's actual controls, configured provider and visible screen review. This update does not establish universal automation of every app.

Validation uses synthetic recipients and mocks; no owner messages are sent as tests. Public YouTube search is checked independently of account sessions.
