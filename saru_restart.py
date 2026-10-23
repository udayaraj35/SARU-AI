"""Restart only this SARU installation after its original process has exited."""
from pathlib import Path
import os,subprocess,sys
import psutil


def gui_python(executable):
    path=Path(executable)
    sibling=path.with_name('pythonw.exe')
    return str(sibling if sibling.is_file() else path)


def schedule_restart(root,parent_pid,executable=sys.executable,popen=subprocess.Popen):
    root=Path(root).resolve()
    if not (root/'app.py').is_file() or not (root/'launch_saru.py').is_file():raise ValueError('SARU installation is incomplete; repair before restarting.')
    helper=root/'saru_restart.py'
    if not helper.is_file() or helper.is_symlink():raise ValueError('SARU restart helper is unavailable.')
    return popen([gui_python(executable),str(helper),'--wait-for',str(int(parent_pid))],cwd=str(root),creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0),close_fds=True)


def restart_after_exit(parent_pid,root=None,executable=sys.executable,process_factory=psutil.Process,popen=subprocess.Popen):
    root=Path(root or Path(__file__).resolve().parent).resolve()
    if parent_pid<=0 or parent_pid==os.getpid():raise ValueError('Invalid SARU parent process.')
    try:process_factory(parent_pid).wait(timeout=45)
    except psutil.NoSuchProcess:pass
    except psutil.TimeoutExpired:return False
    if not (root/'launch_saru.py').is_file():return False
    popen([gui_python(executable),str(root/'launch_saru.py')],cwd=str(root),creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0),close_fds=True)
    return True


if __name__=='__main__':
    if len(sys.argv)!=3 or sys.argv[1]!='--wait-for':raise SystemExit(2)
    raise SystemExit(0 if restart_after_exit(int(sys.argv[2])) else 1)
