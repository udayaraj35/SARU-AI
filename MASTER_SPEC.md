# SARU AI — ULTIMATE MASTER DEVELOPMENT PROMPT
## Advanced Windows Desktop Autonomous AI Assistant
### Complete Project Specification, Migration, Debugging, Integration, Testing and Release Plan

You are a senior Windows desktop software architect, Python engineer, AI agent engineer, cybersecurity engineer, UI/UX designer, voice AI engineer, DevOps engineer, QA tester, and release manager.

Your mission is to transform my existing **SARU AI v17 Windows Desktop Assistant** into a highly advanced, polished, reliable, secure, customizable, voice-enabled, multimodal and task-capable personal AI assistant.

**IMPORTANT: This is an existing project, not a brand-new project.**

Start by reading the entire repository, including `AGENTS.md`, `README.md`, `CODEX_SETUP.md`, existing Python source code, assets, installer scripts, dependencies, configuration files, MYRA guides, update tools, and all project documentation.

Preserve every existing useful feature, fix broken implementations, replace nonfunctional placeholder features with working implementations, and report honestly which capabilities are implemented, tested, restricted, or still pending.

Do not delete or silently discard existing features.

Never claim a feature is functional unless its implementation exists and has passed an appropriate test.

---

# 1. PROJECT IDENTITY

Application name: **SARU AI**

Product type: Advanced personal autonomous AI desktop assistant.

Primary target: Windows 11.

Additional targets: Windows 10, Windows 8.1, Windows 8 and future Windows versions where technically supported.

Note: Windows 9 was never released. Windows 8/8.1 are legacy systems with significant compatibility and security constraints. If modern dependencies cannot support them safely, create a separately documented legacy-compatible build or mark them unsupported. Never falsely claim universal compatibility.

Primary languages:
- Nepali (Devanagari)
- Nepali Romanized
- English
- Bulgarian
- Additional languages through supported speech and AI providers

Assistant name: SARU.

Wake words:
- SARU
- Saru
- Hey Saru

Preferred owner greeting:

**"हजुर सर, भन्नुहोस्। म सुन्दैछु।"**

English equivalent:

"Yes, Sir. I'm listening."

The greeting must be customizable.

The assistant should support respectful, friendly, humorous, emotional, casual and consensual romantic conversation, while being honest that it is an AI.

Do not simulate an exclusive human relationship or use manipulative attachment tactics.

---

# 2. PRIMARY DEVELOPMENT RULES

1. Audit the existing project before changing code.
2. Preserve the original dashboard design and existing SARU identity.
3. Preserve user settings, profiles, API provider configurations, conversation history, memories and chosen avatar images.
4. Maintain backward compatibility with saved settings where possible.
5. Use a migration system for changed settings schemas.
6. Fix duplicate buttons, dead click regions and incorrectly mapped controls.
7. Replace image-only button hotspots with actual responsive UI controls.
8. Keep the UI responsive during network calls, voice operations, updates and PC automation.
9. Never block the main interface thread with long-running tasks.
10. Implement proper exception handling, logging and recovery.
11. Add automated tests for critical functionality.
12. Verify updates and downloaded files before installation.
13. Avoid hidden activity, unauthorized access and uncontrolled code execution.
14. Implement feature detection and clearly communicate unsupported capabilities.
15. Keep all existing features unless deliberately replaced with a tested improvement.

Create a documented, maintainable and modular production-quality codebase.

---

# 3. USER INTERFACE AND VISUAL DESIGN

Use the existing selected SARU dashboard reference image as the primary visual identity.

Design direction:
- Futuristic AI command center
- Dark background
- Neon blue, purple, pink and cyan
- Glassmorphism panels
- Smooth transitions
- Subtle 3D effects
- Premium Windows desktop appearance
- Modern icons
- Rounded corners
- Responsive layout
- Clean readable typography
- Attractive animations without excessive CPU usage

The visual dashboard must contain real interactive UI elements rather than treating a screenshot as the complete interface.

Use the provided dashboard assets, SARU photo assets and application icon.

Allow users to customize the background and avatar independently.

Provide these primary pages within the same application window:

1. Home / Dashboard
2. AI Chat
3. Voice Assistant
4. PC Control
5. System Health
6. Social Media
7. WhatsApp
8. Gmail / Email
9. YouTube
10. Files & Folders
11. Website Studio
12. Developer Tools
13. REA Reverse Engineering
14. MYRA Voice Companion
15. Memory Center
16. Task History
17. Owner Profile
18. API Manager
19. Audio Center
20. Display Center
21. Security Center
22. Appearance
23. Update Center
24. Settings
25. Help / Troubleshooting

Use a clear navigation hierarchy to avoid overcrowding.

All visible buttons, tabs, sliders, inputs and menu items must either perform a real action or be visibly marked unavailable with an explanation.

Implement a consistent Back button and navigation history.

Make the interface scalable across common Windows screen resolutions and DPI settings.

---

# 4. FIX DUPLICATE WINDOW BUTTONS

There must only be one actual set of window controls:

- Minimize
- Maximize / Restore
- Close

Do not display the same controls twice.

Choose one tested implementation:

A. Standard Windows title bar controls.

B. Fully functional custom frameless title bar.

If using a custom title bar, correctly implement:
- Dragging
- Maximizing
- Restoring
- Minimizing
- Closing
- Window resizing
- Minimum dimensions
- Windows Snap compatibility where practical
- Correct maximize bounds across multiple displays
- High-DPI scaling
- Keyboard accessibility
- Proper Windows taskbar behavior

Do not embed fake window controls in the dashboard background image.

Ensure close behavior is configurable:

- Exit completely
- Minimize to system tray
- Ask before exiting

Never leave invisible background processes running unexpectedly.

---

# 5. SARU AVATAR AND IMAGE CUSTOMIZATION

Use SARU's portrait as the assistant's identity.

Provide:
- Circular avatar
- Neon animated ring
- Smiling idle animation
- Listening animation
- Thinking animation
- Speaking animation
- Error animation
- Offline animation
- Muted microphone animation

When silent, display a calm smiling avatar.

When listening, display microphone-reactive waveform animation.

When speaking, display an audio-reactive animation.

The animation should respond to genuine audio state rather than arbitrary labels.

Where possible, synchronize mouth movement with speech output.

Provide reduced-motion support.

In Settings → Appearance, allow users to change:
- Main dashboard background
- Assistant portrait
- Floating assistant portrait
- Circular shortcut icon source
- Avatar border colors
- Animation intensity
- Animation speed
- Theme colors
- Window transparency
- Interface font size
- Light/dark display preference

Support JPG, PNG and WEBP images where possible.

Generate Windows-compatible ICO files from the selected portrait.

Ensure avatar updates do not corrupt older settings.

A changed application icon should update shortcuts through an explicit supported action and explain possible Windows icon-cache delays.

Note that Windows desktop shortcut icons are normally static; put animations inside the application, tray companion, or floating widget rather than falsely promising animated `.ico` shortcuts.

---

# 6. FLOATING SARU AI ASSISTANT

Create an optional floating SARU avatar.

Requirements:
- Circular portrait
- Draggable
- Resizable
- Always-on-top toggle
- Opacity setting
- Screen-edge snapping
- Hide/show option
- Position persistence
- Multi-monitor support
- Click to open conversation
- Right-click settings menu
- Microphone state indicator
- Speaking animation
- Minimize to tray
- No unwanted interference with other windows

Allow completely disabling the floating assistant.

---

# 7. NATURAL TWO-WAY VOICE CONVERSATION

Implement a real voice interaction pipeline.

Support:
- Microphone selection
- Input device testing
- Push-to-talk
- Optional wake-word listening
- Voice activity detection
- Speech-to-text
- AI response generation
- Text-to-speech
- Voice interruption / barge-in where supported
- Silence detection
- Conversation turn management
- Audio device reconnection
- Background voice mode with a clearly visible microphone indicator
- Echo and feedback handling
- Mic mute
- Speaker mute
- Voice volume
- Speech speed
- Voice selection
- Test voice button
- Stop speaking button
- Conversation history

Preferred greeting:

User: "Saru!"

SARU: "हजुर सर, भन्नुहोस्। म सुन्दैछु।"

The assistant should not repeatedly greet after every sentence within an active conversation.

Create a natural dialogue state machine:

IDLE → WAKE DETECTED → LISTENING → THINKING → SPEAKING → IDLE

Also support:
- MUTED
- OFFLINE
- PERMISSION_REQUIRED
- ERROR

The interface must reflect the actual state.

Provide selectable male and female voices.

Support locally available Windows TTS voices and compatible external speech providers.

Clearly distinguish:
- Windows system voices
- Cloud neural voices
- Locally installed voice engines
- MYRA voice capabilities, if legitimately accessible

No fake voice previews.

---

# 8. MYRA VOICE INTEGRATION

Preserve the existing MYRA integration documentation and guides.

Reference repository:

https://github.com/codeninjavik/myra-install-guide

Inspect the available instructions and installed MYRA package.

Determine whether MYRA provides a documented API, Python integration interface, subprocess interface, reusable library or other legitimate extension point.

If available, integrate it properly.

If unavailable, provide a MYRA Companion interface for:
- Installation detection
- Installed version
- Official installation instructions
- Launching MYRA
- Checking official package updates
- Version compatibility
- Troubleshooting
- Optional approved process communication

Do not assume the installation guide repository contains full application source code.

Do not copy protected or inaccessible internal components.

Do not claim MYRA's voice engine is embedded in SARU until this has been verified.

Create an adapter architecture so additional voice engines can be installed later without rebuilding the entire assistant.

---

# 9. MICROPHONE PERMISSION AND AUDIO TROUBLESHOOTING

Fix the existing microphone-related failures.

Identify:
- No microphone detected
- Incorrect default microphone
- Device already in use
- Disabled microphone
- Missing driver
- Audio library failure
- Permission denied
- Unsupported sample rate
- Speech recognition timeout
- Disconnected Bluetooth microphone

Provide clear, actionable errors.

On Windows 10/11, open the correct privacy settings and explain which user-controlled permissions need enabling.

Do not bypass Windows microphone privacy permissions or user consent.

When authorized, configure application-level microphone selection and supported device controls.

Provide microphone test recordings with appropriate privacy controls.

Avoid recording or transmitting audio when the user has disabled listening.

---

# 10. WINDOWS PC CONTROL

Develop a supervised autonomous desktop control engine.

Supported actions should include:
- Open applications
- Close authorized applications
- Switch windows
- Launch browser
- Create folders
- Rename files
- Move files
- Copy files
- Search files
- Open directories
- Create text notes
- Manage downloads
- Take screenshots
- Read supported documents
- Organize selected directories
- Change supported audio settings
- Change supported display settings
- Start approved troubleshooting workflows
- Inspect hardware status
- Start authorized scripts
- Automate supported desktop workflows

Use established Windows APIs and well-maintained automation libraries.

Possible implementations:
- pywinauto
- UI Automation
- Win32 APIs
- PowerShell for appropriate administrative tasks
- pyautogui for carefully bounded interaction
- psutil
- OS-native integrations

Prefer structured application automation over fragile screen-coordinate clicking.

Provide action previews and execution logs.

Never run unknown downloaded scripts automatically.

Do not attempt to defeat Windows UAC, security prompts, browser protections or account permissions.

---

# 11. WINDOWS VOLUME AND BRIGHTNESS

Make dashboard sliders truly interactive.

Allow:
- Speaker volume
- Speaker mute/unmute
- Output device selection
- Input device selection
- Supported microphone input gain
- Brightness adjustment
- Multiple-display selection when supported
- Device refresh
- Audio test
- Brightness test

Use native APIs where supported.

Handle unsupported external monitor brightness controls gracefully.

Do not simply open Windows Settings when the action can be performed directly using a supported and authorized API.

If native control is unavailable, explain the limitation and offer the appropriate Windows settings page.

Preserve device settings carefully.

---

# 12. SYSTEM HEALTH AND PC PROBLEM SOLVING

Provide a functional PC diagnostics dashboard.

Display actual:
- CPU usage
- RAM usage
- Disk space
- Disk health when available
- Network status
- Internet connectivity
- Active network adapter
- Battery level for laptops
- Operating system version
- Audio device availability
- Microphone status
- Startup application information
- Selected hardware information

Avoid hardcoded fake values.

Add troubleshooting workflows for:
- Wi-Fi not appearing
- No internet
- Slow startup
- High CPU usage
- Low storage
- Missing audio
- Microphone failure
- App crashes
- Browser problems
- Windows service issues
- Display/brightness problems
- Dependency errors
- Failed updates

For repairs, use an explain → diagnose → preview → request approval → execute → verify workflow.

Provide backup or rollback where practical.

Do not promise that every hardware or operating-system problem can be repaired automatically.

---

# 13. AUTONOMOUS TASK ENGINE

Create a modular AI agent capable of executing multi-step tasks.

The agent must be able to:
- Understand the user's objective
- Break it into smaller steps
- Select authorized tools
- Execute steps sequentially
- Re-evaluate results
- Recover from errors
- Maintain task state
- Resume interrupted approved work
- Report completion accurately
- Save useful execution history
- Ask clarification when required

Autonomy modes:
- Manual
- Assisted
- Supervised autonomous

Optional configurable unattended workflows are allowed only within narrow, predefined scopes.

For ordinary preauthorized tasks, allow background execution.

For high-impact actions, require fresh owner confirmation.

High-impact examples include:
- Deleting important files
- Sending external messages
- Public social-media posting
- Uploading private files
- Financial transactions
- Installing untrusted software
- Changing security settings
- Destructive system changes
- Sending personal information

The owner must be able to stop an active automation immediately.

Include a visible Emergency Stop control.

Maintain auditable logs.

---

# 14. OWNER VOICE AUTHENTICATION AND SECURITY

Implement optional owner speaker verification where technically feasible.

Recognize that speaker identification is probabilistic and can be fooled by recordings or synthetic voices.

Do not use speaker matching as the only security mechanism for sensitive actions.

Support:
- Owner voice enrollment
- Owner voice verification
- Challenge-response / liveness checks where practical
- Security PIN
- PIN change
- Secure recovery options
- Windows Hello integration where supported
- Failed-attempt throttling
- Session locking
- Approval dialogs
- Security activity history

The owner previously mentioned a PIN in conversation.

**Do not hardcode, repeat, or reuse that exposed PIN.**

Require the owner to choose a fresh secret during installation.

Store it using a proper password hashing algorithm such as Argon2id or another established secure method, never plaintext.

Use Windows DPAPI or an appropriate OS-backed credential store for API secrets.

Provide Settings → Security → Change PIN.

Never let voice matching alone bypass approval for sensitive operations.

---

# 15. AI PROVIDER AND API KEY MANAGER

Support:
- Google Gemini
- OpenAI
- OpenRouter
- Custom compatible AI endpoints

Each provider must have independent:
- API key
- Base URL where applicable
- Selected model
- Connection status
- Test connection function
- Last successful verification
- Error diagnostics

Allow switching providers and models without losing keys.

Support:
- Add API key
- Replace API key
- Delete API key
- Show/hide key
- Select model
- Fetch provider-supported models where available
- Test API
- Set default model
- Fallback model selection
- Connection error handling
- Rate-limit reporting
- Token usage information where available

Do not hardcode model identifiers that may no longer exist.

Do not write secrets to ordinary log files.

Existing legacy settings containing plaintext keys should be migrated securely when feasible.

Preserve a recoverable backup without unnecessarily duplicating exposed secrets.

---

# 16. ONLINE / OFFLINE STATUS

Display whether SARU is:
- Online
- Offline
- Connecting
- Connected to AI provider
- API authentication failed
- Limited connectivity

Separate general internet connectivity from actual AI provider connectivity.

Show meaningful diagnostic messages.

Allow supported offline functions to continue working when the internet is unavailable.

Do not present a static image indicator as live network status.

---

# 17. MEMORY AND PERSONALIZATION

Create reliable local memory management.

SARU should remember useful authorized information, including:
- Preferred assistant settings
- Chosen avatar
- Preferred language
- Preferred voice
- Default AI provider
- Recent approved tasks
- Saved notes
- User-selected folders
- Application preferences
- Task history
- Personalization preferences

Use structured persistent storage such as SQLite.

Add:
- Memory search
- Memory viewer
- Edit memory
- Delete memory
- Export memory
- Import memory
- Backup
- Restore
- Data retention options
- Clear conversation history

Do not secretly retain sensitive content.

Provide user control over what SARU remembers.

Preserve memory across normal software upgrades.

---

# 18. SOCIAL MEDIA AUTOMATION

Build account-authorized social-media tools for:

- Facebook
- Instagram
- TikTok
- YouTube
- Other supported networks

Required workflows:
- Account connection
- Draft posts
- Write captions
- Suggest hashtags
- Prepare images
- Prepare videos
- Create titles
- Create descriptions
- Upload media where supported
- Schedule posts
- Review before publishing
- Publish using authorized APIs or approved browser workflows
- Read publication results
- Report failures

Account features must depend on available platform APIs, required permissions and account eligibility.

Do not bypass platform access controls, CAPTCHA, rate limits or security checks.

Avoid scraping private accounts or automating unauthorized access.

Keep account sessions and credentials protected.

Never claim social posting works merely because the platform's website opens.

---

# 19. WHATSAPP INTEGRATION

Support legitimate WhatsApp workflows such as:
- Opening a conversation
- Preparing a message
- Creating a draft
- Attaching selected media
- Reviewing the recipient
- Sending through supported authorized integrations
- Tracking approved outgoing actions
- Managing templates where supported

Use official WhatsApp Business Platform capabilities when applicable.

For ordinary WhatsApp Web, respect authorization and platform restrictions.

Prevent accidental or bulk unsolicited messages.

Do not send messages without an appropriate user approval or valid preauthorized workflow.

---

# 20. GMAIL AND EMAIL INTEGRATION

Integrate Gmail through supported OAuth authorization.

Features:
- Search mail
- Read messages
- Summarize emails
- Compose drafts
- Suggest replies
- Manage attachments
- Search contacts
- Apply labels where authorized
- Send messages after approval
- Report delivery/API failures

Support configurable email providers if feasible.

Store OAuth tokens securely.

Do not ask users to expose Gmail passwords.

Do not confuse opening Gmail in a browser with actual API integration.

---

# 21. YOUTUBE STUDIO

Support:
- Video preparation
- Upload through approved YouTube APIs
- Title creation
- Description generation
- Thumbnail workflow
- Video metadata
- Playlist selection
- Privacy selection
- Scheduling where supported
- Upload progress
- Upload error handling
- Result URL
- Analytics where available and authorized

Publishing should be explicit and auditable.

---

# 22. WEBSITE AND SOFTWARE DEVELOPMENT

Provide a Website Studio and Developer Agent.

The assistant should help:
- Create websites
- Edit source code
- Generate HTML/CSS/JavaScript
- Build Python projects
- Debug errors
- Inspect project structure
- Run tests
- Work with Git
- Prepare releases
- Explain code
- Refactor safely
- Create backups
- Produce change summaries

For software execution, use isolated working environments whenever practical.

Do not automatically execute unknown repository code or installation scripts without review.

---

# 23. GITHUB INTEGRATION

Support GitHub workflows through authorized credentials or OAuth.

Features:
- Connect account
- View repositories
- Clone authorized repositories
- Search files
- Inspect branches
- Review commits
- Create branches
- Edit project files
- Run tests
- Commit changes
- Create pull requests
- Inspect issues
- Track releases
- Compare versions

Prefer pull-request-based development for important changes.

Do not push untested changes directly into protected branches.

Never store access tokens in source code.

---

# 24. REA REVERSE ENGINEERING TOOLS

Reference repository:

https://github.com/morluto/rea

Investigate the project's current documented capabilities, installation steps, supported environments and licensing.

Integrate through supported official interfaces if available.

Potential permitted tasks:
- Inspect software behavior
- Analyze the owner's own applications
- Understand app architecture
- Inspect authorized binaries
- Examine JavaScript/Electron applications
- Generate technical reports
- Assist with debugging
- Analyze UI behavior
- Understand compatibility problems
- Help migrate legacy code

Do not claim REA gives full access to every application.

Do not bypass DRM, license protection, authentication controls, or access restrictions.

Provide a clear installation status and tool availability display.

Require review before executing third-party code.

---

# 25. SETTINGS SYSTEM

Build one consistent Settings center with these sections:

General:
- Language
- Theme
- Startup behavior
- Notifications
- Background mode

Appearance:
- SARU portrait
- Dashboard background
- Shortcut icon
- Floating avatar
- Animations
- Colors

Voice:
- Wake word
- Voice selection
- Microphone
- Speaker
- Voice speed
- Listening mode
- Voice preview

AI:
- Providers
- API keys
- Models
- Connection tests

PC Control:
- Authorized actions
- Automation permissions
- Default folders
- Device controls

Accounts:
- Facebook
- Instagram
- TikTok
- YouTube
- WhatsApp
- Gmail
- GitHub

Security:
- PIN
- Windows Hello
- Owner verification
- Action approval
- Session controls

Memory:
- Storage
- Export
- Delete
- Backup

Updates:
- Check updates
- Version history
- Official sources
- Auto-check frequency
- Download
- Backup
- Rollback

About:
- Version
- Build
- Dependencies
- System compatibility
- Diagnostics

All Settings pages must work.

Do not keep decorative controls that have no functionality.

---

# 26. INSTALLER AND DESKTOP SHORTCUT

Provide a proper Windows installation experience.

The installer must:
- Show SARU's portrait
- Show product name and version
- Allow installation directory selection
- Allow desktop shortcut selection
- Allow Start Menu shortcut creation
- Allow launch-at-startup selection
- Allow per-user installation where possible
- Explain required permissions
- Detect missing dependencies
- Provide installation progress
- Report installation failures
- Allow safe uninstall
- Preserve user data when upgrading
- Offer backup before significant migrations

Use a Windows-compatible installer system such as Inno Setup, WiX, or another suitable build tool.

Use a reliable signed release process when code signing is available.

Create proper ICO assets.

Avoid leaving the default Python or generic `S` shortcut icon.

Provide a standalone installer for supported Windows systems where feasible.

Do not call a ZIP containing Python scripts a fully tested installer.

---

# 27. AUTOMATIC UPDATE SYSTEM

Design a safe long-term update architecture.

Update categories:
- SARU application
- Supported plugins
- AI provider adapters
- MYRA Companion integration
- REA integration
- Optional voice models
- Optional AI models
- Selected third-party tools
- Compatible dependencies

For SARU updates:
1. Check a configured official SARU release source.
2. Compare installed and available versions.
3. Read release metadata.
4. Validate publisher identity and integrity.
5. Download over HTTPS.
6. Verify cryptographic checksums.
7. Verify release signature where available.
8. Create backup.
9. Stop affected processes safely.
10. Install compatible files.
11. Run migrations.
12. Restart the application.
13. Verify startup.
14. Roll back after failure.
15. Preserve settings and memory.

Allow:
- Manual update
- Automatic update checking
- Automatic verified downloads
- Scheduled maintenance windows
- Explicit user approval before important installs
- Optional auto-install only for trusted, predefined, properly signed update channels

Never blindly install arbitrary files from search results or unverified URLs.

Other application updates should use trusted vendor mechanisms or Windows Package Manager where supported.

Respect administrator permissions and user consent.

Do not promise compatibility with unknown future Windows versions without testing.

---

# 28. PERMISSIONS AND USER CONTROL

Create a Permission Center.

Allow the owner to review:
- Microphone access
- Camera access if applicable
- File access
- Network access
- Browser automation
- Connected accounts
- Windows automation
- Background processes
- Startup configuration
- Notifications
- Screen capture

Explain what each permission enables.

Do not request unnecessary administrator privileges.

Use least-privilege access wherever possible.

Windows privacy controls requiring user interaction must remain user-controlled.

Offer a guided permission setup wizard without bypassing operating-system security.

---

# 29. PERFORMANCE AND RELIABILITY

Optimize for normal Windows laptops and desktops.

Requirements:
- Fast application startup
- Low idle CPU usage
- Controlled memory consumption
- Async networking
- Background workers for long tasks
- Cancelable jobs
- Correct thread handling
- Clean application shutdown
- No resource leaks
- Graceful offline mode
- Crash recovery
- Structured logs
- UI event responsiveness
- Device reconnection

Test high-DPI screens, window resizing, different screen resolutions and multiple monitors.

Avoid allocating unnecessary resources for visual effects.

---

# 30. TESTING AND QUALITY ASSURANCE

Perform a systematic audit of the v17 codebase.

Test at least:
- Python syntax
- Dependency installation
- Application startup
- Dashboard rendering
- Navigation
- Settings
- Profile
- Icon generation
- Shortcut generation
- Window controls
- Avatar appearance
- Floating widget
- Microphone initialization
- Voice input
- Voice output
- Volume control
- Brightness control
- API key storage
- API provider switching
- Offline detection
- Memory persistence
- Backup and restore
- Update verification
- Installer flow
- Windows startup integration
- Safe shutdown
- Failure recovery

Add automated unit and integration tests.

Use mock services for external APIs.

When actual Windows hardware or account testing is not available, clearly mark tests as pending instead of claiming success.

Create a test matrix for Windows 10/11 and separate feasibility documentation for Windows 8/8.1.

---

# 31. USER EXPERIENCE EXAMPLES

Example 1 — Wake word:

User: "Saru!"

SARU: "हजुर सर, भन्नुहोस्। म सुन्दैछु।"

Example 2 — Volume:

User: "Saru, volume 60 percent gara."

SARU adjusts the authorized Windows audio endpoint and reports the actual result.

Example 3 — PC diagnostics:

User: "Saru, mero Wi-Fi dekhaena. Check gara."

SARU inspects available network adapters, runs supported diagnostics, explains the issue and requests approval before repair steps requiring elevated permissions.

Example 4 — Social publishing:

User: "Saru, yo video Facebook ra YouTube ma post gara."

SARU prepares the content, validates connected account permissions, displays a publishing preview, obtains required approval, uploads through supported interfaces and reports the outcome.

Example 5 — Casual conversation:

User: "Saru, malai ramailo kura gara."

SARU responds naturally and respectfully through the selected voice.

Example 6 — Security:

User: "Saru, important files delete gara."

SARU identifies the affected files and consequences, requires stronger verification and explicit confirmation before deletion.

Example 7 — Updates:

User: "Saru, update check gara."

SARU checks configured official sources, verifies available releases and presents safe update options.

---

# 32. PROJECT ARCHITECTURE

Refactor the existing source code into maintainable modules when justified.

Suggested structure:

saru-ai/
- app/
  - main.py
  - ui/
  - assets/
  - core/
  - agents/
  - voice/
  - ai_providers/
  - windows/
  - integrations/
  - security/
  - memory/
  - diagnostics/
  - updater/
  - database/
- installer/
- tests/
- docs/
- scripts/
- requirements/
- AGENTS.md
- README.md
- CHANGELOG.md
- SECURITY.md
- CONTRIBUTING.md
- LICENSE
- .gitignore

This is a suggested architecture, not an instruction to destroy the existing structure.

Migrate incrementally and preserve working code.

---

# 33. GIT AND CODEX WORKFLOW

Treat the supplied SARU AI v17 codebase as the source of truth.

First:
- Inventory all files.
- Identify working and nonworking features.
- Identify security weaknesses.
- Identify missing dependencies.
- Document architectural problems.
- Create a prioritized repair plan.

Then:
- Implement changes in manageable commits.
- Add tests.
- Review regressions.
- Update documentation.
- Maintain a changelog.
- Track known issues.
- Prepare versioned releases.

Use GitHub branches and pull requests where appropriate.

Never overwrite the owner's repository history unnecessarily.

Keep private files, user data and credentials out of public commits.

---

# 34. RELEASE DELIVERABLES

Produce the following deliverables wherever technically feasible:

1. Complete updated SARU source project.
2. Fully documented Windows setup.
3. Windows installer build scripts.
4. Buildable Windows executable distribution.
5. SARU custom icon and avatar assets.
6. Working settings and navigation.
7. Voice assistant module.
8. PC automation module.
9. AI provider management module.
10. Secure settings and memory storage.
11. Approved social integration adapters.
12. MYRA Companion module.
13. REA integration adapter.
14. Windows diagnostics.
15. Update Center.
16. Automated test suite.
17. User manual.
18. Developer documentation.
19. Known limitations report.
20. Versioned release package.

Include a clear distinction between:
- Fully implemented and tested
- Implemented but not hardware-tested
- Requires API credentials or authorization
- Partially implemented
- Not implemented
- Unsupported by the platform

---

# 35. FINAL ACCEPTANCE REQUIREMENTS

The project must not be presented as fully completed until:

- The application launches reliably on supported Windows versions.
- Navigation buttons function correctly.
- Duplicate window controls are gone.
- Settings and Profile open successfully.
- SARU's customized portrait and shortcut icon appear correctly.
- Voice input works on a tested supported microphone.
- Voice output works with a tested available engine.
- Microphone failures are handled gracefully.
- Provider switching works using valid configurations.
- Volume and supported brightness controls are tested.
- User data survives upgrades.
- Installation and uninstall are verified.
- Update rollback is tested.
- Supported automation workflows perform their claimed actions.
- Sensitive actions require appropriate authentication and consent.
- Unsupported social-media actions are not falsely advertised as functional.
- Security issues are addressed.
- No hardcoded credentials remain.
- Documentation reflects the actual implementation.

# FINAL MASTER INSTRUCTION

**Build the best practical version of SARU AI by continuously improving the existing v17 project.**

Preserve its identity, memory, visuals, user settings and previous work.

Fix bugs before adding unstable features.

Prefer reliable working features over attractive nonfunctional buttons.

Use official and trusted integration methods.

Give the owner maximum practical control over their own computer while respecting explicit permissions, account authorization, operating-system security and safe action confirmation.

Do not replace genuine testing with promises.

Start by reading the repository and `AGENTS.md`. Produce a project audit, then implement the highest-priority repairs directly in code. Continue through testing, documentation, packaging and versioned releases.

Do not stop at producing mockups or speculative feature lists.

**The goal is a real, installable, maintainable Windows desktop AI assistant that listens, speaks, remembers, assists, automates approved tasks, diagnoses problems and improves safely over time.**

Project name: **SARU AI**

Development baseline: **SARU AI v17**

Target: **A reliable, modern, extensible AI Personal Desktop Assistant.**
