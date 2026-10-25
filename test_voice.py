import asyncio
import struct
import types
import unittest
from live_voice import PCMBuffer,amplitude,voice_config,LiveVoice

class VoiceTests(unittest.TestCase):
 def test_output_only_saved_microphone_uses_default_without_changing_preferences(self):
  from live_voice import usable_audio_device
  audio=types.SimpleNamespace(query_devices=lambda value:{'max_input_channels':0 if value==2 else 2,'max_output_channels':2})
  events=[];emit=lambda *event:events.append(event)
  self.assertEqual(usable_audio_device(audio,2,'input',emit),-1)
  self.assertEqual(usable_audio_device(audio,1,'input',emit),1)
  self.assertEqual(usable_audio_device(audio,2,'output',emit),2)
  self.assertEqual(len(events),1)
 def test_pcm_playback_and_interrupt(self):
  buf=PCMBuffer(16);buf.append(b'1234');self.assertEqual(buf.read(6),(b'1234\0\0',4));buf.append(b'abc');buf.clear();self.assertEqual(len(buf),0)
  self.assertFalse(buf.append(b'x'*17));self.assertEqual(len(buf),0)
 def test_amplitude_is_real(self):
  self.assertEqual(amplitude(b'\0'*8),0);self.assertAlmostEqual(amplitude(struct.pack('<h',16384)),.5)
 def test_start_requires_own_key_and_live_model(self):
  with self.assertRaises(ValueError):LiveVoice({},lambda *args:None).start()
  with self.assertRaises(ValueError):LiveVoice({'keys':{'Gemini':'synthetic'}},lambda *args:None).start()
 def test_live_configuration(self):
  cfg=voice_config({'live_voice':'Aoede','voice_language':'ne-NP'})
  self.assertEqual(cfg['response_modalities'],['AUDIO']);self.assertIn('separate command interface',cfg['system_instruction'])

class SessionTests(unittest.IsolatedAsyncioTestCase):
 async def test_wake_mode_blocks_background_audio_history_and_commands(self):
  events=[];pcm=b'\0'*1280;finished=asyncio.Event()
  class Stream:
   def __enter__(self):return self
   def __exit__(self,*args):pass
  audio=types.SimpleNamespace(check_input_settings=lambda **kw:None,check_output_settings=lambda **kw:None,RawInputStream=lambda **kw:Stream(),RawOutputStream=lambda **kw:Stream())
  class Session:
   async def send_realtime_input(self,**kwargs):pass
   async def receive(self):
    for text in ['open Chrome','SARU open Chrome','phone conversation','SARU hello','open WhatsApp']:
     c=types.SimpleNamespace(interrupted=False,input_transcription=types.SimpleNamespace(text=text,finished=True),output_transcription=types.SimpleNamespace(text='reply'),model_turn=types.SimpleNamespace(parts=[types.SimpleNamespace(inline_data=types.SimpleNamespace(data=pcm))]),turn_complete=True)
     yield types.SimpleNamespace(server_content=c)
    finished.set();await asyncio.Event().wait()
  class Connection:
   async def __aenter__(self):return Session()
   async def __aexit__(self,*args):pass
  async def close():pass
  client=types.SimpleNamespace(aio=types.SimpleNamespace(live=types.SimpleNamespace(connect=lambda **kw:Connection()),aclose=close))
  engine=LiveVoice({'keys':{'Gemini':'synthetic'},'live_model':'test','wake_word_required':True,'live_headphones':True},lambda *event:events.append(event),lambda key:client,audio)
  task=asyncio.create_task(engine.run())
  try:
   await asyncio.wait_for(finished.wait(),2)
   self.assertEqual([e[1][0] for e in events if e[0]=='conversation_turn'],['SARU open Chrome','SARU hello'])
   self.assertEqual(len([e for e in events if e[0]=='output_level']),1)
   self.assertFalse(any('phone conversation' in str(e) for e in events))
  finally:
   engine.stop()
   try:await task
   except asyncio.CancelledError:pass
 async def test_finalized_command_dispatches_before_model_finishes_once(self):
  events=[];release=asyncio.Event()
  class Stream:
   def __enter__(self):return self
   def __exit__(self,*args):pass
  audio=types.SimpleNamespace(check_input_settings=lambda **kw:None,check_output_settings=lambda **kw:None,RawInputStream=lambda **kw:Stream(),RawOutputStream=lambda **kw:Stream())
  def content(text='',finished=False,complete=False):
   return types.SimpleNamespace(server_content=types.SimpleNamespace(input_transcription=types.SimpleNamespace(text=text,finished=finished),output_transcription=None,model_turn=None,turn_complete=complete,interrupted=False))
  class Session:
   async def send_realtime_input(self,**kwargs):pass
   async def receive(self):
    yield content('open ')
    self.before_final=[e for e in events if e[0]=='conversation_turn']
    yield content('Google Chrome',True)
    await release.wait()
    yield content(complete=True)
    await asyncio.Event().wait()
  session=Session()
  class Connection:
   async def __aenter__(self):return session
   async def __aexit__(self,*args):pass
  async def close():pass
  client=types.SimpleNamespace(aio=types.SimpleNamespace(live=types.SimpleNamespace(connect=lambda **kw:Connection()),aclose=close))
  engine=LiveVoice({'keys':{'Gemini':'synthetic'},'live_model':'test','live_headphones':True,'wake_word_required':False},lambda *event:events.append(event),lambda key:client,audio)
  task=asyncio.create_task(engine.run())
  try:
   for _ in range(100):
    await asyncio.sleep(.01)
    if any(e[0]=='conversation_turn' for e in events):break
   self.assertEqual(session.before_final,[])
   self.assertEqual([e[1] for e in events if e[0]=='conversation_turn'],[('open Google Chrome','')])
   release.set();await asyncio.sleep(.02)
   self.assertEqual(len([e for e in events if e[0]=='conversation_turn']),1)
  finally:
   engine.stop()
   try:await task
   except asyncio.CancelledError:pass
 async def test_playback_burst_is_paced_without_losing_samples(self):
  engine=LiveVoice({},lambda *args:None);engine.playback=PCMBuffer(16)
  original=bytes(range(100));heard=bytearray()
  async def device():
   while len(heard)<len(original):
    data,count=engine.playback.read(4);heard.extend(data[:count]);await asyncio.sleep(.001)
  await asyncio.wait_for(asyncio.gather(engine.queue_playback(original),device()),2)
  self.assertEqual(bytes(heard),original);self.assertEqual(len(engine.playback),0)
 async def test_backpressure_stops_and_detects_a_stalled_device(self):
  engine=LiveVoice({},lambda *args:None);engine.playback=PCMBuffer(16)
  engine.playback.append(b'x'*16)
  with self.assertRaisesRegex(RuntimeError,'device stopped'):await engine.queue_playback(b'xx',stall_seconds=.02)
  task=asyncio.create_task(engine.queue_playback(b'xx'));await asyncio.sleep(.01);engine.stop_event.set();await asyncio.wait_for(task,.2)
 async def test_two_turns_audio_transcripts_and_cleanup(self):
  events=[];sent=[];closed=[];pcm=struct.pack('<h',3000)*640
  class Stream:
   def __init__(self,kind,callback):self.kind=kind;self.callback=callback
   def __enter__(self):
    if self.kind=='output':self.callback(bytearray(1920),960,None,'output underflow')
    if self.kind=='input':self.callback(pcm,640,None,None)
    return self
   def __exit__(self,*args):closed.append(self.kind)
  audio=types.SimpleNamespace(check_input_settings=lambda **kw:None,check_output_settings=lambda **kw:None,RawInputStream=lambda **kw:Stream('input',kw['callback']),RawOutputStream=lambda **kw:Stream('output',kw['callback']))
  class Session:
   def __init__(self):self.turn=0
   async def send_realtime_input(self,**kwargs):sent.append(kwargs)
   async def receive(self):
    if self.turn<3:
     self.turn+=1
     content=types.SimpleNamespace(interrupted=self.turn==2,input_transcription=types.SimpleNamespace(text='एप खोल्नुहोस्' if self.turn==3 else 'hello'),output_transcription=types.SimpleNamespace(text='I cannot access your PC' if self.turn==3 else 'reply '+str(self.turn)),model_turn=types.SimpleNamespace(parts=[types.SimpleNamespace(inline_data=types.SimpleNamespace(data=pcm))]),turn_complete=True)
     yield types.SimpleNamespace(server_content=content)
    else:await asyncio.Event().wait()
  class Connection:
   async def __aenter__(self):return Session()
   async def __aexit__(self,*args):closed.append('session')
  async def close_client():closed.append('client')
  client=types.SimpleNamespace(aio=types.SimpleNamespace(live=types.SimpleNamespace(connect=lambda **kw:Connection()),aclose=close_client))
  engine=LiveVoice({'keys':{'Gemini':'synthetic'},'live_model':'test-live','live_headphones':True,'wake_word_required':False},lambda *event:events.append(event),lambda key:client,audio)
  task=asyncio.create_task(engine.run())
  for _ in range(100):
   await asyncio.sleep(.01)
   if len([e for e in events if e[0]=='conversation_turn'])>=3 and any('audio' in item for item in sent):break
  self.assertEqual(len([e for e in events if e[0]=='transcript' and e[1][0]=='SARU']),2)
  self.assertEqual([e[1] for e in events if e[0]=='conversation_turn'],[('hello','reply 1'),('hello','reply 2'),('एप खोल्नुहोस्','')])
  self.assertEqual(len([e for e in events if e[0]=='output_level']),2)
  self.assertTrue(any('audio' in item for item in sent));engine.stop()
  self.assertTrue(any(event[0]=='audio_warning' for event in events))
  with self.assertRaises(asyncio.CancelledError):await task
  self.assertEqual(set(closed),{'input','output','session','client'});self.assertEqual(len(engine.playback),0)

if __name__=='__main__':unittest.main()
