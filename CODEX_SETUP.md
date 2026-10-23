# Codex setup

Application sources are in this directory. Read MASTER_SPEC.md, DEVELOPMENT_STATUS.md and SECURITY.md first. No AGENTS.md was supplied in the original project. Preserve AppData and existing assets; do not include secrets or user memory in packages.

Python 3.11 on Windows 10/11 is the supported development baseline. Install requirements.txt in an isolated virtual environment. Run python -m unittest discover -v, then python smoke_gui.py on Windows with desktop permission. Tests must not use real account credentials.

python package_source.py generates a verified ZIP plus SHA256 in dist/. build_exe.bat is an optional PyInstaller build recipe requiring an independently installed build tool and dependencies. It has not been executed or validated as a standalone executable release. No signing identity is configured. Do not label source packages as fully tested installers.
