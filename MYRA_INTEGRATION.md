# MYRA integration for SARU v14

MYRA installation guide: https://github.com/codeninjavik/myra-install-guide
Official published package: `myra-ai-assistant` on PyPI. Its source is not included in the guide repository.

In SARU Settings open **MYRA Voice Companion / official update**. Check status, launch installed MYRA, or approve an update. Updates use `python -m pip install --upgrade myra-ai-assistant` in SARU's Python environment. If MYRA is installed under a different Python environment, its existing command may still launch but updates need to be run with that environment's Python.

**Security**: SARU never runs arbitrary downloaded GitHub scripts automatically. Package installation needs explicit approval. Review third-party code and maintain backups. This version does not embed MYRA audio into SARU, migrate MYRA settings, or guarantee voice conversation from the SARU dashboard.

**Auto update**: To avoid silent execution of unverified third-party code, package changes require approval. SARU's own release checking still needs a configured trusted repository. Persistent SARU data remains in `%APPDATA%\SARU_AI`.

Windows 10/11 targeted; Windows 8/8.1 and future releases unverified.

Version 15 includes the complete uploaded MYRA installation guide in MYRA_OFFICIAL_GUIDES. Open it from Settings > MYRA Voice Companion.
