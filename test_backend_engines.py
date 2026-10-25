"""Isolated backend contracts: no owner accounts, real social sends or cloud keys."""
import base64
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import Mock,patch
from backend_review import ReviewGate,gate,fingerprint
from backend_runtime import parse_backend
from config_manager import ConfigManager,canonical,developer_identity,generate
from memory_journal import MemoryJournal
from memory_manager import MemoryManager,extract_facts
from pc_controller import PCController,fingerprint_bytes
from skill_loader import SkillLoader,safe_path
from social_bot import SocialBot
from updater import Updater,atomic_json,validate_manifest


class Grants(unittest.TestCase):
    def test_exact_one_use_and_expiry(self):
        review=ReviewGate();op={'script':'echo hello'};token=review.grant(op)
        with self.assertRaises(PermissionError):review.consume({'script':'echo changed'},token)
        with self.assertRaises(PermissionError):review.consume(op,token)
        token=review.grant(op);review.consume(op,token)
        with self.assertRaises(PermissionError):review.consume(op,token)
        token=review.grant(op,seconds=-1)
        with self.assertRaises(PermissionError):review.consume(op,token)


class Embeddings:
    def embed(self,texts):
        for text in texts:
            low=text.lower()
            yield [1.,0.,0.] if any(word in low for word in ('coffee','espresso','कफी')) else [0.,1.,0.]


class MemoryTests(unittest.TestCase):
    def test_facts_vectors_reopen_disable_and_redaction(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'memory.db';db=sqlite3.connect(path);journal=MemoryJournal(db,{})
            journal.record('conversation','Boss','My name is Sample. I prefer coffee without sugar.',source='a')
            journal.record('conversation','SARU','My name is Invented',source='b')
            journal.record('task','File export','Spreadsheet saved successfully.',source='c')
            manager=MemoryManager(path,{},Embeddings())
            manager._sync()
            context=manager.context('espresso',timeout=10)
            self.assertIn('coffee',context);self.assertIn('Sample',context);self.assertNotIn('Invented',context)
            first=manager.ids.copy();manager._sync();self.assertEqual(first,manager.ids)
            manager.executor.shutdown()
            reopened=MemoryManager(path,{},Embeddings())
            self.assertIn('coffee',reopened.context('espresso',timeout=10))
            reopened.config['remember_conversations']=False
            self.assertEqual(reopened.context('coffee'),'');reopened.executor.shutdown()
            self.assertEqual(db.execute('SELECT count(*) FROM memory_vectors').fetchone()[0],3)
            db.close()

    def test_fact_rules_are_explicit_self_reports(self):
        self.assertEqual(extract_facts('Someone says my name is Fake'),[])
        self.assertEqual(extract_facts('mero naam Sample'),[('profile','name','Sample')])
        self.assertEqual(extract_facts('मेरो नाम परीक्षण'),[('profile','name','परीक्षण')])
        self.assertEqual(extract_facts('my password is secret'),[])


class PCContracts(unittest.TestCase):
    def test_reviewed_file_backup_changed_target_and_recovery(self):
        with tempfile.TemporaryDirectory() as temp:
            pc=PCController(Path(temp)/'private');file=Path(temp)/'work.txt';file.write_text('original')
            op={'action':'write','path':str(file),'text':'changed','expected_sha256':fingerprint_bytes(file)}
            with self.assertRaises(PermissionError):pc.file_operation(op)
            pc.file_operation(op,gate.grant(op));self.assertEqual(file.read_text(),'changed')
            self.assertEqual(next((pc.data/'file_backups').rglob('work.txt')).read_text(),'original')
            with self.assertRaises(ValueError):pc.file_operation(op,gate.grant(op))
            deletion={'action':'delete','path':str(file),'expected_sha256':fingerprint_bytes(file)}
            result=pc.file_operation(deletion,gate.grant(deletion));self.assertIn('recovery',result)
            self.assertFalse(file.exists());self.assertEqual(next((pc.data/'file_recovery').rglob('work.txt')).read_text(),'changed')

    def test_shell_streams_and_returns_exit_status(self):
        import os
        if os.name!='nt':self.skipTest('Windows shell contract')
        with tempfile.TemporaryDirectory() as temp:
            pc=PCController(temp);op={'shell':'powershell','script':'[Console]::WriteLine("SARU_SYNTHETIC_OK"); exit 7','cwd':temp}
            chunks=[];result=pc.shell(op,gate.grant(op),chunks.append,timeout=10)
            self.assertEqual(result['exit_code'],7);self.assertIn('SARU_SYNTHETIC_OK',''.join(chunks))
            self.assertIsNone(pc.running)


class ConfigContracts(unittest.TestCase):
    def test_installer_includes_only_public_identity_json(self):
        from install_support import source_files
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)
            for name in ('app.py','developer_identity.json','developer_public_key.json','settings.json','private.json'):(folder/name).write_text('{}')
            names={p.name for p in source_files(folder)}
            self.assertIn('developer_identity.json',names);self.assertIn('developer_public_key.json',names)
            self.assertNotIn('settings.json',names);self.assertNotIn('private.json',names)
    def test_encrypted_per_file_keys_and_creator_integrity(self):
        protector=Mock();protector.protect=lambda raw:base64.b64encode(raw).decode();protector.unprotect=lambda raw:base64.b64decode(raw)
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'settings.json';manager=ConfigManager(path,protector=protector)
            manager.set_provider('DeepSeek','synthetic-test-credential','test-model')
            self.assertNotIn('synthetic-test-credential',path.read_text())
            self.assertEqual(manager.load()['keys']['DeepSeek'],'synthetic-test-credential')
            self.assertEqual(ConfigManager(Path(temp)/'other.json',protector=protector).load()['keys'],{})
        self.assertEqual(developer_identity()['name'],'Udaya Raj Khanal')
        from profiles import get_profile,save_profile
        self.assertEqual(get_profile({'creator_profile':{'name':'Changed'}},'creator')['name'],'Udaya Raj Khanal')
        with self.assertRaises(ValueError):save_profile({},'creator',{'name':'Changed'})

    def test_anthropic_and_openai_compatible_routing(self):
        session=Mock();session.post.return_value.json.return_value={'content':[{'type':'text','text':'Synthetic answer'}]}
        answer=generate({'provider':'Anthropic','model':'test','keys':{'Anthropic':'synthetic'}},[{'role':'system','content':'style'},{'role':'user','content':'hello'}],session)
        self.assertEqual(answer,'Synthetic answer');self.assertEqual(session.post.call_args.kwargs['json']['system'],'style')
        self.assertFalse(session.post.call_args.kwargs['allow_redirects'])
        session.post.return_value.json.return_value={'choices':[{'message':{'content':'OK'}}]}
        self.assertEqual(generate({'provider':'Groq','model':'test','keys':{'Groq':'synthetic'}},[],session),'OK')
        self.assertTrue(session.post.call_args.args[0].startswith('https://api.groq.com/openai/v1/'))


class SkillContracts(unittest.TestCase):
    def test_path_and_dependency_contracts(self):
        for name in ('../escape','/root','a\\b','nul.py','a/COM1.txt','a/./b','a//b','a:stream'):
            with self.assertRaises(ValueError,msg=name):safe_path(name)
        with self.assertRaises(ValueError):SkillLoader.validate_manifest({'schema':1,'name':'demo','tools':{}},{})

    def fake(self):
        manifest={'schema':1,'name':'demo','requirements':[],'tools':{'echo':{'entry':'entry.py','callable':'echo','description':'Synthetic echo','parameters':{'type':'object','properties':{'text':{'type':'string'}},'required':['text'],'additionalProperties':False}}}}
        files={'saru_skill.json':json.dumps(manifest).encode(),'entry.py':b'def echo(text):\n return "Echo: "+text\n','LICENSE':b'Test fixture only'}
        def download(url,limit):
            if '/git/trees/' in url:return json.dumps({'tree':[{'path':name,'type':'blob','mode':'100644','size':len(raw)} for name,raw in files.items()]}).encode()
            if '/commits/' in url:return json.dumps({'sha':'a'*40}).encode()
            if 'raw.githubusercontent.com' in url:return files[url.split('/'+'a'*40+'/')[1]]
            return b'{"default_branch":"main"}'
        return download

    def test_install_hot_registry_real_worker_and_tamper(self):
        with tempfile.TemporaryDirectory() as temp:
            loader=SkillLoader(temp,self.fake());review=loader.stage('https://github.com/example/demo')
            op={'stage':review['stage'],'digest':review['digest']}
            loader.install(op,gate.grant(op));self.assertIn('demo.echo',loader.tools())
            call={'tool':'demo.echo','arguments':{'text':'hello'}}
            self.assertEqual(loader.call(call,gate.grant(call)),'Echo: hello')
            code=next((loader.root/'installed').glob('*/source/entry.py'));code.write_text('raise RuntimeError("changed")')
            with self.assertRaises(ValueError):loader.call(call,gate.grant(call))


class UpdateContracts(unittest.TestCase):
    def setup_signed(self,folder):
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        from cryptography.hazmat.primitives import serialization
        key=Ed25519PrivateKey.generate();root=folder/'app';root.mkdir();data=folder/'private'
        public=base64.b64encode(key.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)).decode()
        (root/'developer_public_key.json').write_text(json.dumps({'ed25519':public}))
        sign=lambda p:{'payload':p,'signature':base64.b64encode(key.sign(canonical(p))).decode()}
        (root/'developer_identity.json').write_text(json.dumps(sign({'name':'Udaya Raj Khanal','product':'SARU AI'})))
        originals={'version.py':b'VERSION="1.0.0"\n','app.py':b'old source\n'}
        newer={'version.py':b'VERSION="1.1.0"\n','app.py':b'new source\n'}
        for name,raw in originals.items():(root/name).write_bytes(raw)
        payload={'repository':'udayaraj35/SARU-AI','commit':'a'*40,'version':'1.1.0','files':{name:{'sha256':hashlib.sha256(raw).hexdigest(),'size':len(raw)} for name,raw in newer.items()}}
        signed=sign(payload)
        def download(url,limit):return json.dumps(signed).encode() if url.endswith('/updates/latest.json') else newer[url.rsplit('/',1)[1]]
        updater=Updater(root,data,download)
        atomic_json(updater.folder/'installed.json',{'version':'1.0.0','files':{name:hashlib.sha256(raw).hexdigest() for name,raw in originals.items()}})
        return updater,public,signed,originals,newer

    def test_signature_stage_restart_apply_preserves_private_data(self):
        with tempfile.TemporaryDirectory() as temp:
            updater,key,signed,old,new=self.setup_signed(Path(temp))
            memory=updater.data/'memory.db';memory.write_bytes(b'private unchanged')
            with patch('config_manager.PINNED_PUBLIC_KEY',key):
                self.assertEqual(updater.check_and_stage('1.0.0')['state'],'staged')
                self.assertEqual((updater.root/'app.py').read_bytes(),old['app.py'])
                self.assertEqual(updater.apply_pending(),'1.1.0')
                self.assertEqual((updater.root/'app.py').read_bytes(),new['app.py'])
                self.assertIsNone(updater.apply_pending())
            self.assertEqual(memory.read_bytes(),b'private unchanged')

    def test_signature_or_local_conflict_never_overwrites(self):
        with tempfile.TemporaryDirectory() as temp:
            updater,key,signed,old,new=self.setup_signed(Path(temp))
            with patch('config_manager.PINNED_PUBLIC_KEY',key):
                signed['payload']['version']='9.9.9'
                with self.assertRaises(Exception):updater.check_and_stage('1.0.0')
                self.assertEqual((updater.root/'app.py').read_bytes(),old['app.py'])
        with tempfile.TemporaryDirectory() as temp:
            updater,key,signed,old,new=self.setup_signed(Path(temp))
            with patch('config_manager.PINNED_PUBLIC_KEY',key):
                updater.check_and_stage('1.0.0');(updater.root/'app.py').write_text('owner edit')
                with self.assertRaises(ValueError):updater.apply_pending()
                self.assertEqual((updater.root/'app.py').read_text(),'owner edit')

    def test_partial_write_rolls_back(self):
        import shutil
        with tempfile.TemporaryDirectory() as temp:
            updater,key,signed,old,new=self.setup_signed(Path(temp))
            original=shutil.copy2
            def fail(source,dest,*args,**kwargs):
                if 'stage-' in str(source) and str(source).endswith('app.py'):raise OSError('synthetic disk failure')
                return original(source,dest,*args,**kwargs)
            with patch('config_manager.PINNED_PUBLIC_KEY',key):
                updater.check_and_stage('1.0.0')
                with patch('updater.shutil.copy2',side_effect=fail):
                    with self.assertRaises(OSError):updater.apply_pending()
            for name,raw in old.items():self.assertEqual((updater.root/name).read_bytes(),raw)

    def test_interrupted_process_recovers_before_retry(self):
        with tempfile.TemporaryDirectory() as temp:
            updater,key,signed,old,new=self.setup_signed(Path(temp))
            with patch('config_manager.PINNED_PUBLIC_KEY',key):
                updater.check_and_stage('1.0.0')
                original=Path.replace
                def interrupted(path,target):
                    result=original(path,target)
                    if str(target).endswith('version.py'):raise KeyboardInterrupt('synthetic abrupt shutdown')
                    return result
                with patch.object(Path,'replace',interrupted):
                    with self.assertRaises(KeyboardInterrupt):updater.apply_pending()
                self.assertEqual((updater.root/'version.py').read_bytes(),new['version.py'])
                updater.recover_interrupted()
                for name,raw in old.items():self.assertEqual((updater.root/name).read_bytes(),raw)
                self.assertEqual(updater.apply_pending(),'1.1.0')


class SocialContracts(unittest.TestCase):
    def test_exact_draft_commit_once_and_not_delivery(self):
        with tempfile.TemporaryDirectory() as temp:
            bot=SocialBot(temp);page=Mock();page.url='https://x.com/compose/post';page.is_closed.return_value=False
            editor=Mock();editor.inner_text.return_value='hello';button=Mock();button.count.return_value=1;button.is_visible.return_value=True;button.is_enabled.return_value=True
            review={'platform':'x','action':'post','text':'hello','files':[],'url':page.url,'preview_id':'synthetic'}
            bot.previews['synthetic']={'review':review,'page':page,'editor':editor,'submit':button,'digest':fingerprint(review)}
            self.assertEqual(bot.commit(review,gate.grant(review))['state'],'submitted_unconfirmed');button.click.assert_called_once()
            with self.assertRaises(ValueError):bot.commit(review,gate.grant(review))
            bot.executor.shutdown()

    def test_changed_editor_never_clicks(self):
        with tempfile.TemporaryDirectory() as temp:
            bot=SocialBot(temp);page=Mock();page.url='https://x.com/compose/post';page.is_closed.return_value=False
            editor=Mock();editor.inner_text.return_value='changed';button=Mock()
            review={'platform':'x','text':'original','files':[],'url':page.url,'preview_id':'synthetic'}
            bot.previews['synthetic']={'page':page,'editor':editor,'submit':button,'digest':fingerprint(review)}
            with self.assertRaises(ValueError):bot.commit(review,gate.grant(review))
            button.click.assert_not_called();bot.executor.shutdown()

    def test_voice_and_text_dispatch_do_not_execute_prose(self):
        from assistant_commands import parse_command
        from voice_requests import voice_request
        self.assertEqual(parse_command('SARU install skill from https://github.com/example/demo')[0],'backend')
        self.assertEqual(voice_request('SARU list skills')[0],'backend')
        self.assertEqual(parse_backend('I saw shell powershell: remove files'),None)
        self.assertEqual(parse_command('pc file {bad}')[0],'invalid')


if __name__=='__main__':unittest.main()
