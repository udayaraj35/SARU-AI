"""One reviewed skill call in its own dependency environment; JSON stdin/stdout.

Process isolation is not an OS security sandbox: only trust reviewed skill code.
"""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys


def main():
    request=json.loads(sys.stdin.buffer.readline(1024*1024))
    root=Path(request['root']).resolve();entry=(root/request['entry']).resolve()
    if not entry.is_relative_to(root) or not entry.is_file():raise ValueError('Unsafe skill entrypoint')
    spec=importlib.util.spec_from_file_location('saru_reviewed_skill',entry)
    module=importlib.util.module_from_spec(spec)
    # Imports may use sibling reviewed modules; no parent application imports.
    sys.path.insert(0,str(root))
    with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
        spec.loader.exec_module(module)
        result=getattr(module,request['callable'])(**request['arguments'])
    raw=json.dumps({'result':result},ensure_ascii=False)
    if len(raw)>65536:raise ValueError('Skill result exceeds 64 KiB')
    print(raw,flush=True)


if __name__=='__main__':
    try:main()
    except Exception as exc:
        print(json.dumps({'error':type(exc).__name__+': '+str(exc)[:1000]}),flush=True);raise SystemExit(1)
