import asyncio,json,sqlite3,tempfile,types,unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import AsyncMock,Mock
from memory_journal import MemoryJournal,live_lookup
from live_voice import LiveVoice

class JournalTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.folder=Path(self.temp.name);self.path=self.folder/'memory.db';self.db=sqlite3.connect(self.path)
  self.db.execute('CREATE TABLE messages(id INTEGER PRIMARY KEY,role TEXT,content TEXT)');self.db.execute('CREATE TABLE notes(id INTEGER PRIMARY KEY,title TEXT,content TEXT)')
  self.config={'remember_conversations':True,'keys':{'Gemini':'synthetic-credential-value'}};self.memory=MemoryJournal(self.db,self.config)
 def tearDown(self):self.db.close();self.temp.cleanup()
 def test_migration_is_incremental_preserves_original_and_survives_restart(self):
  self.db.execute("INSERT INTO messages VALUES(1,'Boss','मेरो मनपर्ने रंग गुलाबी हो')");self.db.execute("INSERT INTO notes VALUES(1,'Preference','tea without sugar')");self.db.commit()
  self.memory.sync(self.folder);self.memory.sync(self.folder)
  self.assertEqual(self.memory.counts(),{'conversation':1,'note':1});self.assertIn('गुलाबी',live_lookup(self.path,self.config,'गुलाबी'))
  self.assertEqual(self.db.execute('SELECT content FROM messages').fetchone()[0],'मेरो मनपर्ने रंग गुलाबी हो')
 def test_actual_task_results_and_partial_log_tail(self):
  file=self.folder/'agent_tasks.jsonl';first=json.dumps({'command':'open Example','action':'launch','result':'failed: not installed'})+'\n'
  file.write_text(first+'{"command":',encoding='utf8');self.memory.sync(self.folder);self.assertEqual(self.memory.counts()['task'],1)
  file.write_text(first+json.dumps({'command':'open Chrome','action':'launch','result':'opened verified window'})+'\n',encoding='utf8')
  self.memory.sync(self.folder);self.assertEqual(self.memory.counts()['task'],2);self.assertIn('failed',self.memory.context('Example'))
 def test_disabled_retains_existing_and_explicit_note_but_stops_automatic_writes(self):
  self.memory.record('task','done','completed');self.config['remember_conversations']=False
  self.memory.record('task','hidden','new task');self.memory.record('note','explicit','owner requested note',explicit=True)
  self.db.execute("INSERT INTO messages VALUES(1,'Boss','not imported')");self.db.commit();self.memory.sync(self.folder)
  self.assertEqual(self.memory.counts(),{'note':1,'task':1});self.assertIn('disabled',live_lookup(self.path,self.config,'completed'))
 def test_credentials_excluded_from_recording_and_retrieval(self):
  self.memory.record('conversation','Boss','value synthetic-credential-value');self.memory.record('task','status','password is not-for-memory')
  text=str(self.memory.search());self.assertNotIn('synthetic-credential-value',text);self.assertNotIn('not-for-memory',text)
 def test_query_ranking_filter_bound_and_sql_metacharacters(self):
  self.memory.record('task','purple report','purple status');self.memory.record('conversation','Boss','purple shoes')
  self.assertEqual(self.memory.search('purple report',1)[0]['title'],'purple report')
  self.assertEqual(len(self.memory.search('purple',100,'task')),1);self.assertEqual(self.memory.search("%'; DROP TABLE memory_journal;--"),[])
  self.assertLessEqual(len(self.memory.context('purple')),6505)
 def test_office_state_updates_and_export_paths_are_searchable_without_duplicates(self):
  (self.folder/'office').mkdir()
  with closing(sqlite3.connect(self.folder/'office/office.db')) as other:
   other.execute('CREATE TABLE jobs(id,task,state,result,review,error)');other.execute('CREATE TABLE exports(job,path,format)')
   other.execute("INSERT INTO jobs VALUES('j1','Kathmandu report','working',NULL,NULL,NULL)");other.execute("INSERT INTO exports VALUES('j1','D:/Work/report.pdf','pdf')")
   other.commit()
  self.memory.sync(self.folder)
  with closing(sqlite3.connect(self.folder/'office/office.db')) as other:other.execute("UPDATE jobs SET state='ready',result='verified draft'");other.commit()
  self.memory.sync(self.folder);self.assertEqual(self.memory.counts(),{'file':1,'office':1});self.assertIn('ready',self.memory.context('Kathmandu'))
 def test_new_work_is_available_to_long_running_voice_lookup(self):
  self.assertIn('No matching',live_lookup(self.path,self.config,'saffron'))
  self.memory.record('task','Saffron shopping','Owner saved the saffron list')
  self.assertIn('saffron list',live_lookup(self.path,self.config,'saffron'))
 def test_unreadable_optional_office_does_not_break_existing_memory(self):
  self.memory.record('note','Safe note','existing preference');(self.folder/'office').mkdir();(self.folder/'office/office.db').write_bytes(b'corrupt optional file')
  self.memory.sync(self.folder);self.assertTrue(self.memory.sync_warnings);self.assertIn('existing preference',self.memory.context('preference'))
  self.assertIn('could not be synchronized',live_lookup(self.path,self.config,'preference'))

class LiveMemoryTests(unittest.IsolatedAsyncioTestCase):
 async def test_same_event_transcript_authorizes_only_current_addressed_memory_call(self):
  for text,expected in [('SARU what tea do I like?',True),('phone conversation',False)]:
   done=asyncio.Event();lookup=Mock(return_value='tea without sugar');session=types.SimpleNamespace(send_tool_response=AsyncMock(),send_realtime_input=AsyncMock());configs=[]
   call=types.SimpleNamespace(id='lookup',name='recall_local_memory',args={'query':'tea'})
   async def receive():
    yield types.SimpleNamespace(tool_call=types.SimpleNamespace(function_calls=[call]),server_content=types.SimpleNamespace(input_transcription=types.SimpleNamespace(text=text,finished=True),output_transcription=None,interrupted=False,model_turn=None,turn_complete=False))
    done.set();await asyncio.Event().wait()
   session.receive=receive
   class Stream:
    def __enter__(self):return self
    def __exit__(self,*args):pass
   class Connection:
    async def __aenter__(self):return session
    async def __aexit__(self,*args):pass
   def connect(**kw):configs.append(kw['config']);return Connection()
   client=types.SimpleNamespace(aio=types.SimpleNamespace(live=types.SimpleNamespace(connect=connect),aclose=AsyncMock()))
   audio=types.SimpleNamespace(check_input_settings=Mock(),check_output_settings=Mock(),RawInputStream=lambda **kw:Stream(),RawOutputStream=lambda **kw:Stream())
   engine=LiveVoice({'keys':{'Gemini':'synthetic'},'live_model':'test'},Mock(),lambda key:client,audio,memory_lookup=lookup)
   task=asyncio.create_task(engine.run())
   try:
    await asyncio.wait_for(done.wait(),3);self.assertEqual(lookup.called,expected);self.assertEqual(configs[0]['tools'][0]['function_declarations'][0]['behavior'],'BLOCKING');session.send_tool_response.assert_awaited_once()
   finally:
    engine.stop()
    try:await task
    except asyncio.CancelledError:pass
 async def test_lookup_is_read_only_current_turn_authorized_and_disabled_aware(self):
  lookup=Mock(return_value='saved preference');engine=LiveVoice({'remember_conversations':True},Mock(),memory_lookup=lookup);session=types.SimpleNamespace(send_tool_response=AsyncMock())
  call=types.SimpleNamespace(id='one',name='recall_local_memory',args={'query':'tea'})
  await engine.resolve_memory_calls(session,[call],False);lookup.assert_not_called();self.assertIn('error',session.send_tool_response.call_args.kwargs['function_responses'][0]['response'])
  await engine.resolve_memory_calls(session,[call],True);lookup.assert_called_once_with('tea')
  self.assertEqual(session.send_tool_response.call_args.kwargs['function_responses'][0]['response']['memory_data'],'saved preference')
  engine.settings['remember_conversations']=False;await engine.resolve_memory_calls(session,[call],True);self.assertEqual(lookup.call_count,1)
 async def test_model_cannot_use_memory_interface_as_arbitrary_tool(self):
  lookup=Mock();engine=LiveVoice({},Mock(),memory_lookup=lookup);session=types.SimpleNamespace(send_tool_response=AsyncMock())
  await engine.resolve_memory_calls(session,[types.SimpleNamespace(id='bad',name='run_shell',args={'query':'anything'})],True);lookup.assert_not_called()

if __name__=='__main__':unittest.main()
