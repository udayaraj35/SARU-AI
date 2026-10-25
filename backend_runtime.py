"""Hooks into existing text/voice command dispatch; no new UI or styling."""
import json
from pathlib import Path
import queue
import re
import threading
from backend_review import gate,fingerprint
from config_manager import developer_identity
from pc_controller import PCController,fingerprint_bytes
from skill_loader import SkillLoader
from social_bot import SocialBot


def parse_backend(text):
    from voice_gate import strip_address
    q=strip_address(str(text)).strip()
    match=re.fullmatch(r'(?:install skill from|skill install)\s+(https://github\.com/\S+)',q,re.I)
    if match:return ('skill_install',match[1])
    match=re.fullmatch(r'(?:run )?shell (powershell|cmd|bash)\s*:\s*([\s\S]+)',q,re.I)
    if match:return ('shell',{'shell':match[1].lower(),'script':match[2]})
    match=re.fullmatch(r'(?:run skill|skill run)\s+([a-z][a-z0-9_]*\.[a-z][a-z0-9_]*)\s+(\{[\s\S]*\})',q,re.I)
    if match:return ('skill_run',{'tool':match[1].lower(),'arguments':json.loads(match[2])})
    if q.casefold() in ('list installed skills','list skills','skill list'):return ('skill_list',None)
    if q.casefold() in ('memory engine status','semantic memory status'):return ('memory_status',None)
    if q.casefold() in ('stop shell','shell stop'):return ('shell_stop',None)
    if q.casefold() in ('check signed updates','check backend updates'):return ('update',None)
    match=re.fullmatch(r'social open (whatsapp|facebook|instagram|x)',q,re.I)
    if match:return ('social_open',match[1].lower())
    if q.casefold()=='social whatsapp unread':return ('social_unread',None)
    match=re.fullmatch(r'social whatsapp read\s+(.+)',q,re.I)
    if match:return ('social_read',match[1])
    match=re.fullmatch(r'social (\{[\s\S]*\})',q,re.I)
    if match:return ('social',json.loads(match[1]))
    match=re.fullmatch(r'pc file (\{[\s\S]*\})',q,re.I)
    if match:return ('file',json.loads(match[1]))
    return None


class BackendRuntime:
    def __init__(self,root,source,data,config,offer,report):
        self.root=root;self.source=Path(source);self.data=Path(data);self.config=config
        self.offer=offer;self.report=report;self.events=queue.Queue();self.closed=False
        self.pc=PCController(data);self.skills=SkillLoader(data);self.social=SocialBot(data,bool(config.get('social_stealth',True)))
        self.integrity_error=''
        try:developer_identity(source)
        except Exception as exc:self.integrity_error='Developer integrity check failed: '+type(exc).__name__
        root.after(100,self.poll)

    def poll(self):
        if self.closed:return
        try:
            for _ in range(30):
                kind,value=self.events.get_nowait()
                if kind=='callback':value()
                else:self.report(str(value))
        except queue.Empty:pass
        self.root.after(100,self.poll)

    def job(self,work,done=None):
        def run():
            try:
                result=work()
                if done:self.events.put(('callback',lambda value=result:done(value)))
                else:self.events.put(('result',json.dumps(result,ensure_ascii=False,indent=2) if not isinstance(result,str) else result))
            except Exception as exc:
                from memory_journal import clean
                self.events.put(('result','Backend action failed: '+clean(str(exc),self.config)[:1600]))
        threading.Thread(target=run,daemon=True).start()

    def reviewed(self,operation,callback,description):
        def approved():
            if self.integrity_error:raise PermissionError(self.integrity_error)
            # Reverify at use time: installation may have been edited since startup.
            developer_identity(self.source)
            token=gate.grant(operation)
            self.job(lambda:callback(operation,token))
            return 'Reviewed action started; actual results follow in chat.'
        return self.offer(description,approved)

    def handle(self,request):
        action,arg=request
        if action=='shell_stop':self.pc.stop();return 'Stop requested for SARU’s own command process.'
        if action=='memory_status':
            from memory_manager import manager
            return manager(self.data/'memory.db',self.config).status
        if action=='skill_list':return json.dumps(self.skills.tools(),ensure_ascii=False,indent=2)
        if action=='shell':
            operation={**arg,'cwd':str(self.data)}
            self.reviewed(operation,lambda op,token:self.pc.shell(op,token,lambda part:self.events.put(('result','Shell output: '+part))), 'Run this exact '+arg['shell']+' script as your Windows user:\n'+arg['script'])
            return 'Shell script prepared for review.'
        if action=='file':
            if arg['action']=='read':self.job(lambda:self.pc.file_operation(arg));return 'Reading the requested text file.'
            operation=dict(arg)
            path=Path(arg['path'])
            if arg['action'] in ('write','delete','move') and path.is_file():operation['expected_sha256']=fingerprint_bytes(path)
            self.reviewed(operation,self.pc.file_operation,'File change (existing files backed up/recoverable):\n'+json.dumps(operation,ensure_ascii=False))
            return 'File operation prepared for review.'
        if action=='skill_install':
            def staged(review):
                operation={'stage':review['stage'],'digest':review['digest']}
                description=('Install trusted Python skill '+review['repo']+' at '+review['commit']+'\nTools: '+', '.join(review['tools'])+'\nDependencies: '+', '.join(review['dependencies'])+'\nReview source: '+str(self.skills.root/'staged'/review['stage']/'source')+'\nSkill code runs with your Windows-user rights. Digest: '+review['digest'])
                self.reviewed(operation,self.skills.install,description)
            self.job(lambda:self.skills.stage(arg),staged)
            return 'Fetching pinned skill source and manifest; no code is executing.'
        if action=='skill_run':
            self.reviewed(arg,self.skills.call,'Run registered skill with these exact arguments:\n'+json.dumps(arg,ensure_ascii=False))
            return 'Skill invocation prepared for review.'
        if action in ('social_open','social_unread','social_read'):
            method={'social_open':'open','social_unread':'unread','social_read':'read_chat'}[action]
            self.job(lambda:self.social.submit(method,*(() if arg is None else (arg,))).result(timeout=70))
            return 'Opening the requested local social session; account login may be required.'
        if action=='social':
            if arg.get('action')=='open':
                self.job(lambda:self.social.submit('open_profile',arg['platform'],arg['target']).result(timeout=70))
                return 'Opening the requested social profile.'
            def ready(review):
                self.reviewed(review,lambda op,token:self.social.submit('commit',op,token).result(timeout=30),'Review exact social action and visible account/draft:\n'+json.dumps(review,ensure_ascii=False)+'\nDelivery will not be claimed from a click alone.')
            self.job(lambda:self.social.submit('prepare',arg).result(timeout=90),ready)
            return 'Preparing a visible social draft; final submission awaits review.'
        if action=='update':
            from updater import Updater
            from version import VERSION
            self.job(lambda:Updater(self.source,self.data).check_and_stage(VERSION) or 'No newer signed source update.')
            return 'Checking signed source updates.'
        raise ValueError('Unknown backend command')

    def close(self):
        self.closed=True;self.pc.stop();self.social.submit('close')
