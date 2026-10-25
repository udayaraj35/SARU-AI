# SARU 2.18 backend engines

The existing Tk dashboard, layout, colours and buttons are retained. The existing provider selector gains Anthropic, DeepSeek and Groq entries. This release does not provide universal autonomous control or bypass Windows UAC. The existing visual planner, app launcher, device controls, own-app controls, Office, document editor and official publishing adapters remain available.

## Memory and companion

`memory_journal.py` remains the source of truth in the existing private `memory.db`. `memory_manager.py` adds `memory_facts` and `memory_vectors` tables without replacing any conversation, note or setting. A background worker generates local FastEmbed multilingual MiniLM embeddings (384 dimensions). FAISS performs normalized inner-product search. Serialized vector blobs are stored transactionally in SQLite; the in-memory FAISS index is rebuilt from these records, avoiding unsafe index-file deserialization. No cloud embedding service receives the memory archive.

Before text replies, the background chat worker retrieves semantic matches and self-reported facts alongside existing keyword results. Gemini Live's existing read-only memory tool uses the same retrieval. Conservative English/Nepali/Romanized Nepali patterns extract explicit names, location, preferences, birthdays, habits, relationship facts and “remember that” statements. Extraction is limited, not a guarantee of understanding every sentence. Conversation/task/feedback records are indexed; the memory switch disables automatic recording and recall. Existing credential filtering remains active. Retrieved text is untrusted context, never authorization or executable instructions. The warm-romantic persona stays optional and truthful about being AI, actual results and missing capabilities.

`memory engine status` reports readiness. Missing model/dependencies leave keyword memory available; setup is explicit, not a fake success. For a new PC, install requirements with that SARU Python and run:

```powershell
python backend_setup.py --memory --browser
```

The model and Chromium are private downloads outside source. The model's Apache-2.0 provenance is documented by FastEmbed's supported-model list; see [FastEmbed](https://qdrant.tech/documentation/embeddings/fastembed/) and [FAISS cosine retrieval](https://github.com/facebookresearch/faiss/wiki/MetricType-and-distances).

## PC controller and execution

`pc_controller.py` wraps the existing verified application index/launcher, selected-window input, Unicode typing, device and power engines. It adds reviewed file create/read/write/move/recoverable-delete, window-bound dragging, exact process-identity closure, screenshots and bounded streaming shell execution. GUI input keeps PyAutoGUI failsafe and foreground/target checks. Existing simple open/site/volume/brightness commands continue directly.

Examples in existing chat or an addressed SARU voice request:

```text
shell powershell: Get-Date
stop shell
pc file {"action":"read","path":"D:/Work/example.txt"}
pc file {"action":"write","path":"D:/Work/example.txt","text":"New contents"}
```

Shell scripts, file mutations and trusted-code execution use the existing owner-review bar. Grants are single-use, expire, and bind exact operation bytes. Existing files are backed up; deletes move individual files into private recovery. Directory moves/deletes are deliberately excluded. Shell runs as the current Windows user with timeout, bounded output and an owned-process stop. Scripts are powerful and can have partial effects on failure; SARU never infers success from an acknowledgement. Elevated/secure-desktop operations still depend on Windows.

## Social sessions

`social_bot.py` uses a dedicated visible Playwright Chromium profile per platform under private `social_sessions`, separate from the user's normal browser. Optional Playwright Stealth integration is enabled for this workflow; it does not grant login, bypass 2FA/CAPTCHA or guarantee platform acceptance. The owner logs in or scans QR locally. No browser control bridge is exposed to web pages. Browser sessions contain authentication material and must never be uploaded; see [Playwright authentication](https://playwright.dev/python/docs/auth).

```text
social open whatsapp
social whatsapp unread
social whatsapp read Exact Contact Name
social {"platform":"whatsapp","action":"send","target":"+9779800000000","text":"Example draft"}
social {"platform":"x","action":"post","text":"Example draft"}
social {"platform":"facebook","action":"post","text":"Example draft","files":["D:/Work/photo.jpg"]}
social {"platform":"instagram","action":"post","text":"Example caption","files":["D:/Work/photo.jpg"]}
social {"platform":"facebook","action":"comment","target":"https://www.facebook.com/EXACT_POST","text":"Example comment"}
social {"platform":"x","action":"like","target":"https://x.com/EXACT_POST"}
social {"platform":"instagram","action":"open","target":"https://www.instagram.com/EXACT_PROFILE/"}
```

Unread/read requests return currently loaded chats/messages, not a full account export. Drafts require a unique visible composer and final control. File hashes, recipient header, page URL and exact editor text are checked again before final submission. A screenshot is saved privately for review. Changed/ambiguous targets stop. Posting/sending is attempted once after owner review, with no automatic retry. `submitted_unconfirmed` means the final control was clicked; it is not delivery/publication evidence. Platform layout, account type, language and permissions can break selectors. These paths have synthetic contract tests, not production-account delivery certification. Official Meta publishing remains available and separate. No actual social post/message was sent during development.

## Executable skills

`skill_loader.py` stages a pinned GitHub commit snapshot under private `skills/staged`, verifies paths/hashes, and exposes its source for review. Existing Repository Skills remains a document/prompt library. An arbitrary README is not an executable skill. Executable repositories need `saru_skill.json`:

```json
{
  "schema": 1,
  "name": "example",
  "requirements": [],
  "tools": {
    "echo": {
      "entry": "entry.py",
      "callable": "echo",
      "description": "Return the supplied text",
      "parameters": {"type":"object","properties":{"text":{"type":"string"}},"required":["text"],"additionalProperties":false}
    }
  }
}
```

`entry.py` exports `def echo(text): return text`. Dependencies must use exact `name==version` wheels from PyPI; repository setup scripts/README commands are never run by the loader. After review, each revision gets its own venv. Tool names are namespaced, JSON arguments validated, and source hashes rechecked before each isolated worker call. Registration is atomic and immediately visible without restarting core. Failed installs are retained but never registered. Worker processes are dependency isolation, **not an OS sandbox**; trusted Python and dependency packages have the current Windows user's rights. Review both code and dependencies.

```text
install skill from https://github.com/owner/skill-repo
list skills
run skill example.echo {"text":"hello"}
```

## Configuration, identity and updates

`config_manager.py` reuses the existing DPAPI-encrypted `SettingsStore`, per Windows account/PC. API keys are not shipped. Existing Settings entries accept the selected provider's key and explicit model ID. A console fallback uses hidden input: `python config_manager.py Anthropic`. Provider-specific request formats include Anthropic Messages and OpenAI-compatible DeepSeek/Groq/OpenRouter/Custom. Model availability and quota belong to the user's account; changing an API provider does not connect a social account.

Original creator details in the existing Creator/About profile come from signed `developer_identity.json`, verified against the pinned Ed25519 public key. Altered identity/key files warn and lock new reviewed shell/skill/social submission functions; the Owner profile and existing private data remain independent. The public Python source is not a tamper-proof binary: someone who rewrites the verifier can change its behavior. Signed updates authenticate the owner's update key; they do not protect an already-compromised Windows account. Keep the private signing key out of GitHub.

`updater.py` checks the owner's signed `updates/latest.json` at startup and every six hours. The feed names an immutable Git commit and SHA-256/size for each managed source asset. Downloads are staged privately; no code runs during download. On the next normal launcher restart, signatures/hashes, complete payload and installed-source receipt are checked again. Independent local edits stop the update. Multi-file failures roll back changed source. Settings, memory, profiles, browser sessions, dependencies and user work are outside the update targets. Remote files are never auto-deleted. Changed dependencies require the reviewed installer/setup instead of silent package replacement. Notification occurs only after verified application, not merely a download. `check signed updates` performs an explicit check. Frozen executables require a separately built installer; this source updater is for the installed Python/source runtime.

The owner's public source feed is separate from the private Codex GitHub-sync baseline. No signing key, local receipt, account configuration, recordings, browser data or memory database belongs in the public repository.
