"""Signed immutable-commit source updates, staged privately and applied on restart.

No installer execution, arbitrary hooks, deletion, dependency upgrades, or data wipes.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import threading
import time
from urllib.parse import quote
from config_manager import verify_signed,developer_identity
from repo_library import bounded_get
from skill_loader import safe_path

REPOSITORY='udayaraj35/SARU-AI'
FEED='https://raw.githubusercontent.com/'+REPOSITORY+'/main/updates/latest.json'
ALLOWED={'.py','.png','.jpg','.jpeg','.webp','.svg','.ico','.json','.md','.txt','.bat','.ps1','.html','.css','.js'}


def atomic_json(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+'.tmp')
    with temp.open('w',encoding='utf8') as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2);stream.flush();os.fsync(stream.fileno())
    temp.replace(path)


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_manifest(payload):
    if payload.get('repository')!=REPOSITORY or not re.fullmatch('[0-9a-f]{40}',payload.get('commit','')):raise ValueError('Untrusted update repository/commit')
    if not re.fullmatch(r'\d+\.\d+\.\d+',payload.get('version','')):raise ValueError('Invalid update version')
    files=payload.get('files',{})
    if not 1<=len(files)<=1000:raise ValueError('Invalid update file count')
    seen=set()
    for name,record in files.items():
        safe_path(name);parts=Path(name).parts
        if any(p.startswith('.') for p in parts) or name.casefold() in seen:raise ValueError('Unsafe/colliding update path')
        seen.add(name.casefold())
        if Path(name).suffix.lower() not in ALLOWED or any(p.casefold() in ('profiles','memory','data','recordings','browser_profiles','settings.json','developer_public_key.json') for p in parts):raise ValueError('Update targets protected/local data')
        if not re.fullmatch('[0-9a-f]{64}',record.get('sha256','')) or type(record.get('size')) is not int or not 0<=record['size']<=12*1048576:raise ValueError('Invalid update digest/size')
    if sum(r['size'] for r in files.values())>80*1048576:raise ValueError('Update exceeds 80 MiB')
    if 'version.py' not in files:raise ValueError('Update has no version.py')
    return payload


class Updater:
    def __init__(self,root,data,download=bounded_get):
        self.root=Path(root).resolve();self.data=Path(data).resolve();self.download=download
        self.folder=self.data/'signed_updates';self.folder.mkdir(parents=True,exist_ok=True)

    def check_and_stage(self,current):
        developer_identity(self.root)
        signed=json.loads(self.download(FEED,2*1048576));payload=validate_manifest(verify_signed(signed,self.root))
        version=lambda v:tuple(map(int,v.split('.')))
        if version(payload['version'])<=version(current):return None
        receipt=self.folder/'installed.json'
        if not receipt.exists():raise ValueError('No installed-source receipt. Repair/install this SARU version before automatic patching.')
        installed=json.loads(receipt.read_text(encoding='utf8'))
        stage=self.folder/('stage-'+payload['commit']);stage.mkdir(exist_ok=True)
        changed={}
        for name,record in payload['files'].items():
            target=self.root/name
            if target.is_symlink() or not target.resolve().is_relative_to(self.root):raise ValueError('Unsafe installed path')
            if target.is_file() and digest(target)==record['sha256']:continue
            previous=installed.get('files',{}).get(name)
            if target.exists() and (not previous or digest(target)!=previous):raise ValueError('Local source edit conflicts with update: '+name)
            if name=='requirements.txt':raise ValueError('This update changes dependencies; use its reviewed installer first')
            raw=self.download('https://raw.githubusercontent.com/'+REPOSITORY+'/'+payload['commit']+'/'+quote(name,safe='/'),max(1,record['size']+1))
            if len(raw)!=record['size'] or hashlib.sha256(raw).hexdigest()!=record['sha256']:raise ValueError('Update bytes failed verification: '+name)
            dest=stage/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
            changed[name]={'before':digest(target) if target.exists() else None,'after':record['sha256']}
        atomic_json(stage/'signed_manifest.json',signed)
        atomic_json(self.folder/'pending.json',{'stage':stage.name,'changes':changed,'version':payload['version']})
        return {'state':'staged','version':payload['version'],'files':len(changed),'applies':'next normal restart'}

    def apply_pending(self):
        self.recover_interrupted()
        pending=self.folder/'pending.json'
        if not pending.exists():return None
        developer_identity(self.root)
        job=json.loads(pending.read_text(encoding='utf8'))
        if not re.fullmatch('stage-[0-9a-f]{40}',job['stage']):raise ValueError('Invalid staged update')
        stage=self.folder/job['stage']
        signed=json.loads((stage/'signed_manifest.json').read_text(encoding='utf8'))
        payload=validate_manifest(verify_signed(signed,self.root))
        if job['version']!=payload['version'] or job['stage']!='stage-'+payload['commit']:raise ValueError('Staged identity mismatch')
        changes=job['changes']
        receipt_path=self.folder/'installed.json'
        installed=json.loads(receipt_path.read_text(encoding='utf8'))
        for name,record in changes.items():
            safe_path(name)
            if name not in payload['files'] or record['after']!=payload['files'][name]['sha256']:raise ValueError('Unsigned staged file')
            target=self.root/name
            if not target.resolve().is_relative_to(self.root) or target.is_symlink():raise ValueError('Unsafe update target')
            actual=digest(target) if target.is_file() else None
            if actual!=record['before'] or actual!=installed.get('files',{}).get(name):raise ValueError('Source changed after staging: '+name)
            if digest(stage/name)!=record['after']:raise ValueError('Staged file changed: '+name)
        # Require a complete payload, not a tampered subset of pending.json.
        for name,record in payload['files'].items():
            if name not in changes and (not (self.root/name).is_file() or digest(self.root/name)!=record['sha256']):raise ValueError('Missing staged update file: '+name)
        backup=self.folder/('backup-'+str(time.time_ns()));backup.mkdir()
        # Durable write-ahead record also permits recovery after process/power loss.
        shutil.copy2(receipt_path,backup/'_installed.json')
        for name in changes:
            target=self.root/name
            if target.exists():
                saved=backup/name;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,saved)
        transaction=self.folder/'transaction.json'
        atomic_json(transaction,{'backup':backup.name,'changes':changes,'phase':'applying'})
        replaced=[]
        try:
            for name in changes:
                target=self.root/name
                if target.exists():
                    saved=backup/name;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,saved)
                target.parent.mkdir(parents=True,exist_ok=True)
                temp=target.with_name(target.name+'.saru-update');shutil.copy2(stage/name,temp);temp.replace(target);replaced.append(name)
            for name,record in payload['files'].items():
                if digest(self.root/name)!=record['sha256']:raise ValueError('Installed verification failed')
            atomic_json(receipt_path,{'version':payload['version'],'commit':payload['commit'],'files':{name:record['sha256'] for name,record in payload['files'].items()}})
            atomic_json(transaction,{'backup':backup.name,'changes':changes,'phase':'committed','version':payload['version']})
        except Exception:
            for name in reversed(replaced):
                target=self.root/name;saved=backup/name
                if saved.exists():shutil.copy2(saved,target)
                else:target.unlink(missing_ok=True)
            shutil.copy2(backup/'_installed.json',receipt_path)
            transaction.unlink(missing_ok=True)
            raise
        pending.unlink()
        atomic_json(self.folder/'completed.json',{'version':payload['version'],'verified':True,'notified':False})
        transaction.unlink(missing_ok=True)
        return payload['version']

    def recover_interrupted(self):
        marker=self.folder/'transaction.json'
        if not marker.exists():return
        job=json.loads(marker.read_text(encoding='utf8'))
        if not re.fullmatch('backup-[0-9]+',job['backup']):raise ValueError('Invalid update recovery record')
        if job.get('phase')=='committed':
            # Files and receipt were verified before this durable commit marker.
            (self.folder/'pending.json').unlink(missing_ok=True)
            atomic_json(self.folder/'completed.json',{'version':job['version'],'verified':True,'notified':False})
            marker.unlink();return
        backup=self.folder/job['backup']
        for name,record in job['changes'].items():
            safe_path(name);target=self.root/name
            if not target.resolve().is_relative_to(self.root):raise ValueError('Unsafe recovery path')
            actual=digest(target) if target.is_file() else None
            if actual not in (record['before'],record['after']):raise ValueError('Local edit conflicts with interrupted update: '+name)
            saved=backup/name
            if record['before'] is not None and (not saved.is_file() or digest(saved)!=record['before']):raise ValueError('Recovery backup verification failed')
        for name,record in job['changes'].items():
            target=self.root/name;saved=backup/name
            if record['before'] is None:target.unlink(missing_ok=True)
            else:shutil.copy2(saved,target)
        shutil.copy2(backup/'_installed.json',self.folder/'installed.json')
        marker.unlink()

    def background(self,current,config,emit):
        def work():
            try:
                if config.get('signed_auto_updates',True):self.check_and_stage(current)
            except Exception as exc:
                # No network-error popup loop; expose explicit updater status.
                atomic_json(self.folder/'status.json',{'state':'unavailable','error_type':type(exc).__name__,'detail':str(exc)[:300]})
        threading.Thread(target=work,name='saru-update-check',daemon=True).start()
        complete=self.folder/'completed.json'
        if complete.exists():
            receipt=json.loads(complete.read_text(encoding='utf8'))
            if receipt.get('verified') and not receipt.get('notified'):
                emit('माया, SARU '+receipt['version']+' update भएर जाँच पूरा भयो। तपाईंको memory र keys सुरक्षित छन्।')
                receipt['notified']=True;atomic_json(complete,receipt)
