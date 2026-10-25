"""Reliable GUI entry point with persistent, secret-redacted startup diagnostics."""
from pathlib import Path
import faulthandler
import os
import runpy
import sys
import traceback

ROOT=Path(__file__).resolve().parent

def launch():
    os.chdir(ROOT)
    if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
    sdk=ROOT/'.voice-sdk'
    if (sdk/'google'/'genai').is_dir():sys.path.insert(0,str(sdk))
    data=Path(os.getenv('SARU_DATA_DIR') or str(Path(os.getenv('APPDATA',str(Path.home())))/'SARU_AI'))
    data.mkdir(parents=True,exist_ok=True)
    # Apply only a previously downloaded, signature-verified source update.
    # All user settings, keys, browser sessions and memories live outside ROOT.
    try:
        from updater import Updater
        Updater(ROOT,data).apply_pending()
    except Exception as exc:
        from updater import atomic_json
        atomic_json(data/'signed_updates/status.json',{'state':'apply_failed','error_type':type(exc).__name__,'detail':str(exc)[:300]})
    log=data/'startup.log'
    if log.exists() and log.stat().st_size>1_000_000:
        log.replace(data/'startup.previous.log')
    secrets=[]
    try:
        from settings_store import SettingsStore
        secrets=list(SettingsStore(data/'settings.json',{'keys':{}}).load().get('keys',{}).values())
    except Exception:pass
    def record(kind,exc_type,exc,tb):
        detail=''.join(traceback.format_exception(exc_type,exc,tb))
        for secret in secrets:
            if secret:detail=detail.replace(secret,'[redacted]')
        with log.open('a',encoding='utf-8') as output:output.write('\n'+kind+'\n'+detail)
    native=log.open('a',encoding='utf-8');faulthandler.enable(file=native)
    import tkinter as tk
    previous=tk.Tk.report_callback_exception
    def callback(root,exc_type,exc,tb):
        record('UI callback failed',exc_type,exc,tb)
        try:root.title('SARU AI — action failed; see startup.log')
        except Exception:pass
    tk.Tk.report_callback_exception=callback
    try:
        runpy.run_path(str(ROOT/'app.py'),run_name='__main__')
    except SystemExit as exc:
        if exc.code not in (None,0):record('Startup exited',type(exc),exc,exc.__traceback__)
        raise
    except Exception as exc:
        record('Startup failed',type(exc),exc,exc.__traceback__)
        boot=None
        try:
            from startup_screen import current_startup
            boot=current_startup()
        except Exception:pass
        if boot and not boot.closed:boot.fail(type(exc).__name__+' — see startup.log')
        from tkinter import messagebox
        messagebox.showerror('SARU could not start','SARU could not start. Your settings and memory have been preserved.\n\nError type: '+type(exc).__name__+'\nDiagnostic log: '+str(log)+'\n\nRun the updated installer to repair missing files or dependencies. If this followed a self-improvement, open recover_saru.bat in the SARU folder.')
        if boot and not boot.closed:boot.close();boot.root.destroy()
        return 1
    finally:
        tk.Tk.report_callback_exception=previous
        faulthandler.disable();native.close()
    return 0

if __name__=='__main__':raise SystemExit(launch())
