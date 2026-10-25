"""Backend PC operations using existing launch/input/device engines.

No elevation bypass. Shell commands are explicit reviewed scripts, never model prose.
"""
import codecs
import os
from pathlib import Path
import queue
import shutil
import subprocess
import threading
import time
from backend_review import gate, fingerprint
from secret_handling import safe_memory_text, contains_secret


class PCController:
    def __init__(self,data):
        self.data=Path(data);self.running=None;self.lock=threading.Lock()

    def open_app(self,name):
        from app_index import application_index
        from app_launch import launch_and_verify
        matches=application_index.resolve(name)
        if len(matches)!=1:raise ValueError('Choose one installed app: '+', '.join(x.title for x in matches[:12]))
        return launch_and_verify(matches[0])

    def windows(self):
        from desktop_actions import list_windows
        return list_windows()

    def close_app(self,operation,token):
        """Close the exact reviewed process identity, never a name wildcard."""
        gate.consume(operation,token)
        import psutil
        pid=operation['pid']
        if type(pid) is not int or pid in (0,4,os.getpid(),os.getppid()):raise ValueError('Invalid target process')
        process=psutil.Process(pid)
        if process.username()!=psutil.Process().username():raise PermissionError('Choose an application owned by the current Windows user')
        if process.create_time()!=operation['created_at'] or process.exe()!=operation['executable']:raise ValueError('Application identity changed since review')
        process.terminate()
        try:process.wait(timeout=5)
        except psutil.TimeoutExpired:return 'Close requested; the process is still running. No forced retry.'
        return 'Reviewed process closed: '+str(pid)

    def input(self,command,window):
        import pyautogui,win32gui
        from pc_input import perform_input
        return perform_input(command,window,pyautogui,win32gui.GetForegroundWindow)

    def drag(self,window,start,end,duration=.5):
        import pyautogui,win32gui
        if win32gui.GetForegroundWindow()!=window:raise ValueError('Selected window lost focus')
        width,height=pyautogui.size()
        for point in (start,end):
            if len(point)!=2 or any(type(v) is not int for v in point) or not 0<=point[0]<width or not 0<=point[1]<height:raise ValueError('Invalid screen coordinates')
            if win32gui.GetAncestor(win32gui.WindowFromPoint(tuple(point)),2)!=window:raise ValueError('Drag must stay in the selected window')
        pyautogui.FAILSAFE=True;pyautogui.moveTo(*start)
        if win32gui.GetForegroundWindow()!=window:raise ValueError('Selected window lost focus')
        pyautogui.dragTo(*end,duration=max(.2,min(2,float(duration))))
        return 'Drag performed; inspect the screen.'

    def device(self,name,value):
        from pc_telemetry import device_request
        if name not in ('volume','brightness'):raise ValueError('Unsupported device')
        if type(value) is not int or not 0<=value<=100:raise ValueError('Value must be 0–100')
        return device_request('set',name,value)

    def power(self,action):
        from power_control import request_power
        return request_power(action)

    def screenshot(self,destination):
        import pyautogui
        path=self._path(destination)
        if path.exists():raise FileExistsError('Choose a new screenshot destination')
        pyautogui.screenshot().save(path)
        return str(path)

    @staticmethod
    def _path(value):
        path=Path(value).expanduser()
        if not path.is_absolute() or str(value).startswith(('\\\\','//')):raise ValueError('Use an absolute local path')
        return path.resolve()

    def file_operation(self,operation,token=None):
        action=operation['action'];source=self._path(operation['path'])
        if action=='read':
            if source.stat().st_size>1024*1024:raise ValueError('Text read limit is 1 MiB')
            return safe_memory_text(source.read_text(encoding='utf8'))
        gate.consume(operation,token)
        if action=='write':
            text=operation['text']
            if contains_secret(text):raise ValueError('Use encrypted secret storage')
            if source.exists():
                expected=operation.get('expected_sha256')
                if fingerprint_bytes(source)!=expected:raise ValueError('File changed since review')
                saved=self.data/'file_backups'/str(time.time_ns())/source.name
                saved.parent.mkdir(parents=True);shutil.copy2(source,saved)
            source.parent.mkdir(parents=True,exist_ok=True)
            temp=source.with_name(source.name+'.saru-tmp');temp.write_text(text,encoding='utf8');temp.replace(source)
        elif action=='move':
            if source.is_dir():raise ValueError('Choose an individual file, not a directory')
            if fingerprint_bytes(source)!=operation.get('expected_sha256'):raise ValueError('File changed since review')
            target=self._path(operation['destination'])
            if target.exists():raise FileExistsError('Destination already exists')
            shutil.move(str(source),str(target))
        elif action=='delete':
            # Reversible local quarantine; no recursive delete/system cleanup.
            if source.is_dir():raise ValueError('Choose an individual file, not a directory')
            if fingerprint_bytes(source)!=operation.get('expected_sha256'):raise ValueError('File changed since review')
            target=self.data/'file_recovery'/str(time.time_ns())/source.name
            target.parent.mkdir(parents=True);shutil.move(str(source),str(target))
            return 'Moved to recovery: '+str(target)
        elif action=='mkdir':source.mkdir(parents=True,exist_ok=False)
        else:raise ValueError('Unsupported file operation')
        return 'Completed: '+action+' '+str(source)

    def shell(self,operation,token,on_output=lambda value:None,timeout=120):
        gate.consume(operation,token)
        script=operation['script'];kind=operation.get('shell','powershell')
        if not isinstance(script,str) or not script.strip() or len(script)>16000:raise ValueError('Invalid script')
        if contains_secret(script):raise ValueError('Do not pass credentials in shell commands')
        cwd=self._path(operation.get('cwd',str(self.data)))
        if not cwd.is_dir():raise ValueError('Working directory is unavailable')
        if kind=='powershell':
            exe=shutil.which('powershell.exe') or shutil.which('pwsh')
            args=[exe,'-NoProfile','-NonInteractive','-Command',script]
        elif kind=='cmd':args=[os.environ.get('COMSPEC','cmd.exe'),'/d','/s','/c',script]
        elif kind=='bash':args=[shutil.which('bash'),'-c',script]
        else:raise ValueError('Use powershell, cmd or bash')
        if not args[0]:raise ValueError('Requested shell is not installed')
        with self.lock:
            if self.running and self.running.poll() is None:raise RuntimeError('A SARU command is already running')
            process=subprocess.Popen(args,cwd=cwd,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            self.running=process
        events=queue.Queue(maxsize=512)
        def reader():
            try:
                while True:
                    part=process.stdout.read1(2048)
                    if not part:break
                    try:events.put(part,timeout=.2)
                    except queue.Full:pass
            finally:
                try:events.put(None,timeout=.5)
                except queue.Full:pass
        threading.Thread(target=reader,daemon=True).start()
        started=time.monotonic();output=[];size=0;decoder=codecs.getincrementaldecoder('utf8')('replace')
        try:
            while True:
                if time.monotonic()-started>max(1,min(600,timeout)):
                    self.stop();raise TimeoutError('Shell timed out; inspect any partial effects before retrying')
                try:part=events.get(timeout=.1)
                except queue.Empty:
                    if process.poll() is not None:break
                    continue
                if part is None:break
                text=safe_memory_text(decoder.decode(part));size+=len(text)
                if size<=65536:output.append(text);on_output(text)
            code=process.wait(timeout=5)
            return {'exit_code':code,'output':''.join(output),'truncated':size>65536}
        finally:
            if process.poll() is None:self.stop()
            process.stdout.close()
            with self.lock:self.running=None

    def stop(self):
        with self.lock:process=self.running
        if process and process.poll() is None:
            import psutil
            try:
                parent=psutil.Process(process.pid)
                for child in parent.children(recursive=True):
                    try:child.terminate()
                    except psutil.Error:pass
                parent.terminate()
            except psutil.NoSuchProcess:pass


def fingerprint_bytes(path):
    import hashlib
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
