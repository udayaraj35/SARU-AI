"""Pinned GitHub skill staging, exact review, isolated venvs, hot tool registry."""
import hashlib
import json
from pathlib import Path,PurePosixPath
import re
import shutil
import subprocess
import sys
import threading
import uuid
from urllib.parse import quote
from backend_review import gate, fingerprint
from repo_library import repository_name,bounded_get

ROOT=Path(__file__).resolve().parent


def safe_path(name):
    path=PurePosixPath(name)
    if not name or '\\' in name or ':' in name or path.is_absolute() or any(p in ('','..','.') or p.endswith((' ','.')) for p in name.split('/')):raise ValueError('Unsafe skill path')
    if any(p.casefold().split('.')[0] in {'con','nul','aux','prn',*(f'com{i}' for i in range(1,10)),*(f'lpt{i}' for i in range(1,10))} for p in path.parts):raise ValueError('Reserved Windows path')
    return path


class SkillLoader:
    def __init__(self,data,downloader=bounded_get):
        self.root=Path(data)/'skills';self.root.mkdir(parents=True,exist_ok=True)
        self.download=downloader;self.lock=threading.RLock()

    def stage(self,url):
        name=repository_name(url)
        info=json.loads(self.download('https://api.github.com/repos/'+name,1048576))
        sha=json.loads(self.download('https://api.github.com/repos/'+name+'/commits/'+quote(info['default_branch'],safe=''),1048576))['sha']
        if not re.fullmatch('[0-9a-f]{40}',sha):raise ValueError('Invalid Git commit')
        tree=json.loads(self.download('https://api.github.com/repos/'+name+'/git/trees/'+sha+'?recursive=1',8*1048576))
        if tree.get('truncated'):raise ValueError('Skill repository too large')
        entries=tree['tree']
        manifest_entry=next((r for r in entries if r['path']=='saru_skill.json' and r.get('mode')=='100644'),None)
        if not manifest_entry:raise ValueError('This repo has no saru_skill.json executable-tool contract. Use Repository Skills to import its reference documents, or add an adapter manifest.')
        if len(entries)>500:raise ValueError('Use a focused skill repository (at most 500 entries)')
        folder=self.root/'staged'/uuid.uuid4().hex;folder.mkdir(parents=True)
        records={};total=0;seen=set()
        for item in entries:
            path=item['path'];safe_path(path)
            if item.get('type')=='tree':continue
            if item.get('type')!='blob' or item.get('mode') not in ('100644','100755'):raise ValueError('Symlinks/submodules are not supported')
            if path.casefold() in seen:raise ValueError('Case-colliding paths')
            seen.add(path.casefold())
            if any(p.startswith('.') for p in PurePosixPath(path).parts) or path.endswith(('.exe','.dll','.pyd','.db','.env')):raise ValueError('Unsupported hidden/binary/runtime skill file: '+path)
            if item.get('size',0)>2*1048576:raise ValueError('Skill file too large')
            raw=self.download('https://raw.githubusercontent.com/'+name+'/'+sha+'/'+quote(path,safe='/'),2*1048576)
            total+=len(raw)
            if total>16*1048576:raise ValueError('Skill exceeds 16 MiB')
            dest=folder/'source'/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
            records[path]=hashlib.sha256(raw).hexdigest()
        manifest=json.loads((folder/'source/saru_skill.json').read_text(encoding='utf8'))
        self.validate_manifest(manifest,records)
        staged={'repo':name,'commit':sha,'files':records,'manifest':manifest}
        (folder/'review.json').write_text(json.dumps(staged,indent=2),encoding='utf8')
        return {'stage':folder.name,'repo':name,'commit':sha,'tools':list(manifest['tools']),'dependencies':manifest.get('requirements',[]),'digest':fingerprint(staged),'files':list(records)}

    @staticmethod
    def validate_manifest(manifest,files):
        if manifest.get('schema')!=1:raise ValueError('Expected skill schema 1')
        if not re.fullmatch('[a-z][a-z0-9_]{1,47}',manifest.get('name','')):raise ValueError('Invalid skill name')
        tools=manifest.get('tools',{})
        if not isinstance(tools,dict) or not 1<=len(tools)<=25:raise ValueError('Provide 1–25 tools')
        for name,tool in tools.items():
            if not re.fullmatch('[a-z][a-z0-9_]{1,47}',name):raise ValueError('Invalid tool name')
            safe_path(tool['entry'])
            if tool['entry'] not in files or not tool['entry'].endswith('.py'):raise ValueError('Missing Python entrypoint')
            if not re.fullmatch('[a-zA-Z][a-zA-Z0-9_]*',tool['callable']):raise ValueError('Invalid callable')
            if not isinstance(tool.get('description'),str):raise ValueError('Tool needs a description')
            if tool.get('parameters',{}).get('type')!='object':raise ValueError('Tool needs an object JSON schema')
        for requirement in manifest.get('requirements',[]):
            if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*==[0-9][A-Za-z0-9_.+!-]*',requirement):raise ValueError('Dependencies must be exact name==version wheel requirements')

    def _review(self,stage):
        if not re.fullmatch('[0-9a-f]{32}',stage):raise ValueError('Invalid stage ID')
        folder=self.root/'staged'/stage
        review=json.loads((folder/'review.json').read_text(encoding='utf8'))
        for name,digest in review['files'].items():
            safe_path(name)
            if hashlib.sha256((folder/'source'/name).read_bytes()).hexdigest()!=digest:raise ValueError('Skill changed since staging')
        actual={p.relative_to(folder/'source').as_posix() for p in (folder/'source').rglob('*') if p.is_file()}
        if actual!=set(review['files']):raise ValueError('Unexpected files in skill stage')
        self.validate_manifest(review['manifest'],review['files'])
        return folder,review

    def install(self,operation,token):
        gate.consume(operation,token)
        folder,review=self._review(operation['stage'])
        if fingerprint(review)!=operation['digest']:raise ValueError('Skill review changed')
        target=self.root/'installed'/(review['manifest']['name']+'-'+review['commit'][:12])
        if target.exists():raise FileExistsError('This skill revision is already installed')
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copytree(folder/'source',target/'source')
        try:
            subprocess.run([sys.executable,'-m','venv',str(target/'env')],check=True,timeout=90,capture_output=True)
            python=target/'env'/('Scripts/python.exe' if sys.platform=='win32' else 'bin/python')
            requirements=review['manifest'].get('requirements',[])
            if requirements:
                subprocess.run([str(python),'-m','pip','install','--disable-pip-version-check','--no-input','--only-binary=:all:','--index-url','https://pypi.org/simple',*requirements],check=True,timeout=300,capture_output=True)
            # Reverify source after dependency installation; don't import skill in core.
            for name,digest in review['files'].items():
                if hashlib.sha256((target/'source'/name).read_bytes()).hexdigest()!=digest:raise ValueError('Installed source changed')
            with self.lock:
                registry=self.registry();registry[review['manifest']['name']]={'folder':target.name,**review}
                self._save_registry(registry)
        except Exception:
            # Keep failed install for inspection; it is never registered or run.
            raise
        return 'Skill installed and tools registered without a main-app restart: '+review['manifest']['name']

    def registry(self):
        path=self.root/'registry.json'
        return json.loads(path.read_text(encoding='utf8')) if path.exists() else {}

    def _save_registry(self,registry):
        temp=self.root/'registry.tmp';temp.write_text(json.dumps(registry,indent=2),encoding='utf8');temp.replace(self.root/'registry.json')

    def tools(self):
        return {skill+'.'+tool:meta for skill,record in self.registry().items() for tool,meta in record['manifest']['tools'].items()}

    def call(self,operation,token):
        gate.consume(operation,token)
        skill,name=operation['tool'].split('.',1);record=self.registry()[skill]
        target=(self.root/'installed'/record['folder']).resolve()
        if not target.is_relative_to((self.root/'installed').resolve()):raise ValueError('Invalid installed skill path')
        for path,digest in record['files'].items():
            safe_path(path)
            if hashlib.sha256((target/'source'/path).read_bytes()).hexdigest()!=digest:raise ValueError('Installed skill changed; review and reinstall')
        tool=record['manifest']['tools'][name];arguments=operation.get('arguments',{})
        from jsonschema import validate
        validate(arguments,tool['parameters'])
        python=target/'env'/('Scripts/python.exe' if sys.platform=='win32' else 'bin/python')
        request={'root':str(target/'source'),'entry':tool['entry'],'callable':tool['callable'],'arguments':arguments}
        result=subprocess.run([str(python),'-I',str(ROOT/'skill_worker.py')],input=json.dumps(request),capture_output=True,text=True,encoding='utf8',timeout=60,cwd=target/'source')
        if len(result.stdout)>65536:raise ValueError('Skill result too large')
        response=json.loads(result.stdout)
        if result.returncode or 'error' in response:raise RuntimeError(response.get('error','Skill failed'))
        return response['result']
