import asyncio,types,unittest
from unittest.mock import Mock,AsyncMock,patch
import requests
from live_voice import LiveVoice
from voice_gate import merge_transcript
from voice_hub import VoiceHub
from network_status import InternetStatus

class ReplyTests(unittest.IsolatedAsyncioTestCase):
 async def test_split_wake_is_fully_visible_and_bare_greeting_gets_fallback(self):
  events,_,_,_=await self.exercise([{'input':'SA'},{'input':'RU hello?','finished':True,'complete':True}])
  self.assertEqual(''.join(value[1] for kind,value in events if kind=='transcript' and value[0]=='You'),'SARU hello?')
  self.assertIn(('wake_ack',True),events)
  events,_,_,_=await self.exercise([{'input':'hello SARU.','output':'Hello Boss','finished':True,'audio':True,'complete':True}])
  self.assertNotIn(('wake_ack',True),events)
 async def exercise(self,rows,queued=False,ambient=False):
  events=[];finished=asyncio.Event();sent=[];pcm=b'\x01\x02'*20
  class Stream:
   def __enter__(self):return self
   def __exit__(self,*args):pass
  audio=types.SimpleNamespace(check_input_settings=lambda **kw:None,check_output_settings=lambda **kw:None,RawInputStream=lambda **kw:Stream(),RawOutputStream=lambda **kw:Stream())
  pending=asyncio.Queue()
  def response(row):
   return types.SimpleNamespace(server_content=types.SimpleNamespace(interrupted=False,input_transcription=types.SimpleNamespace(text=row['input'],finished=row.get('finished',False)) if 'input' in row else None,output_transcription=types.SimpleNamespace(text=row['output']) if 'output' in row else None,model_turn=types.SimpleNamespace(parts=[types.SimpleNamespace(inline_data=types.SimpleNamespace(data=pcm))]) if row.get('audio') else None,turn_complete=row.get('complete',False)))
  class Session:
   async def send_realtime_input(self,**kw):pass
   async def send_client_content(self,**kw):
    sent.append(kw);await pending.put({'input':'open Chrome' if ambient else '', 'output':'वास्तविक नतिजा','audio':True,'complete':True})
   async def receive(self):
    for row in rows:
     yield response(row)
     if row.get('before_complete'):self.no_early_reply=not sent
     if row.get('expect_played') and engine.queue_playback.await_count==0:raise AssertionError('Confirmed wake must not wait until the entire answer finishes.')
    if not queued:finished.set();await asyncio.Event().wait()
    row=await pending.get();yield response(row);finished.set();await asyncio.Event().wait()
  session=Session()
  class Connection:
   async def __aenter__(self):return session
   async def __aexit__(self,*args):pass
  async def close():pass
  client=types.SimpleNamespace(aio=types.SimpleNamespace(live=types.SimpleNamespace(connect=lambda **kw:Connection()),aclose=close))
  engine=None
  def emit(kind,value):
   events.append((kind,value))
   if queued and kind=='conversation_turn' and value[0]:engine.speak_reply('The selected app failed to open.')
  engine=LiveVoice({'keys':{'Gemini':'synthetic'},'live_model':'test','wake_word_required':True},emit,lambda key:client,audio)
  engine.thread=Mock();engine.thread.is_alive.return_value=True;engine.queue_playback=AsyncMock()
  task=asyncio.create_task(engine.run())
  try:
   await asyncio.wait_for(finished.wait(),3)
   return events,engine.queue_playback.await_count,sent,getattr(session,'no_early_reply',None)
  finally:
   engine.stop()
   try:await task
   except asyncio.CancelledError:pass
 async def test_audio_and_transcript_before_wake_are_recovered(self):
  events,count,_,_=await self.exercise([{'audio':True,'output':'म सुन्दैछु।'},{'input':'SARU','expect_played':True},{'input':'hello','finished':True,'audio':True,'complete':True}])
  self.assertEqual(count,2);self.assertIn(('conversation_turn',('SARU hello','म सुन्दैछु।')),events)
  self.assertIn(('transcript',('SARU','म सुन्दैछु।')),events)
 async def test_background_audio_is_never_released(self):
  events,count,_,_=await self.exercise([{'audio':True},{'input':'phone talking','finished':True,'audio':True,'complete':True}])
  self.assertEqual(count,0);self.assertFalse(any(k=='conversation_turn' for k,v in events));self.assertIn(('wake_wait',True),events)
 async def test_local_command_reply_waits_for_completed_turn_and_uses_same_session(self):
  events,count,sent,early=await self.exercise([{'input':'SARU open Chrome','finished':True,'audio':True,'before_complete':True},{'complete':True}],queued=True)
  self.assertTrue(early);self.assertEqual(count,1);self.assertEqual(len(sent),1);self.assertTrue(sent[0]['turn_complete']);self.assertIn('failed to open',sent[0]['turns']['parts'][0]['text'])
  self.assertEqual(sum(k=='conversation_turn' and v[0]=='SARU open Chrome' for k,v in events),1)
 async def test_inflight_room_transcript_cannot_silence_explicit_reply_or_run_commands(self):
  events,count,sent,_=await self.exercise([{'input':'SARU open Chrome','finished':True},{'complete':True}],queued=True,ambient=True)
  self.assertEqual(count,1);self.assertEqual(len(sent),1)
  self.assertFalse(any(kind=='transcript' and value==('You','open Chrome') for kind,value in events))
  self.assertFalse(any(kind=='conversation_turn' and value[0]=='open Chrome' for kind,value in events))
  self.assertIn(('transcript',('SARU','वास्तविक नतिजा')),events)

class StateTests(unittest.TestCase):
 def test_cumulative_and_split_wake_transcripts(self):
  self.assertEqual(merge_transcript('SARU','hello'),'SARU hello')
  self.assertEqual(merge_transcript('SARU hello','SARU hello maya'),'SARU hello maya')
 def test_online_is_verified_and_cached_not_assumed_from_adapter(self):
  session=Mock();session.get.return_value=types.SimpleNamespace(status_code=204)
  clock=Mock(return_value=1);state=InternetStatus(session,clock)
  self.assertTrue(state.snapshot()['internet_online']);self.assertTrue(state.snapshot()['internet_online']);session.get.assert_called_once()
  clock.return_value=40;session.get.side_effect=requests.ConnectionError('offline')
  self.assertFalse(state.snapshot()['internet_online']);self.assertEqual(session.get.call_count,3)
 def test_captive_redirect_does_not_count_as_online(self):
  session=Mock();session.get.return_value=types.SimpleNamespace(status_code=302,text='login')
  self.assertFalse(InternetStatus(session).snapshot()['internet_online'])
 def test_error_survives_stopped_event_and_private_reply_is_blocked(self):
  root=Mock();hub=VoiceHub(root,{'keys':{'Gemini':'private-test-key'}},Mock());hub.engine=Mock();hub.engine.active=True
  self.assertFalse(hub.speak_reply('Key private-test-key'));hub.engine.speak_reply.assert_not_called()
  hub.emit('error','provider rejected');hub.emit('state','STOPPED');hub.pump();self.assertEqual(hub.state,'ERROR');self.assertEqual(hub.last_error,'provider rejected');hub.close()
 def test_adapter_up_with_failed_internet_stays_red(self):
  from dashboard_ui import Dashboard
  view=types.SimpleNamespace(gauges={},cfg={'theme':'Neon Rose'},hero_theme='Neon Rose',refresh_activity=Mock(),online=Mock(),network=Mock(),scales={})
  with patch('theme_manager.apply_theme'):Dashboard.render(view,{'adapters':['Wi-Fi'],'internet_online':False,'internet_detail':'offline'})
  view.online.configure.assert_called_with(text='● Offline',fg='#ff3b30')

if __name__=='__main__':unittest.main()
