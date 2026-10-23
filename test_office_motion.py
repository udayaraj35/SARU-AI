import tempfile,unittest,threading,json
from office_motion import OfficeMotion
from office_core import Office
from office_observer import OfficeObserver,mind_text

class MotionTests(unittest.TestCase):
 def test_background_job_can_be_cancelled_from_a_new_view(self):
  with tempfile.TemporaryDirectory() as folder:
   office=Office(folder);job=office.create('Write a report');started=threading.Event();release=threading.Event();errors=[]
   def ai(config,instruction,prompt):
    if 'Split the owner job' in instruction:
     agent=json.loads(prompt)['agents'][0]
     return {'assignments':[{'agent':agent['id'],'task':'Draft the report'}]}
    started.set();release.wait(3)
    return {'title':'Report','body':'Draft','tables':[]}
   def work():
    try:office.run(job,{},ai=ai)
    except RuntimeError as exc:errors.append(str(exc))
   thread=threading.Thread(target=work);thread.start()
   try:
    self.assertTrue(started.wait(3));self.assertTrue(Office(folder).cancel_job(job))
   finally:release.set();thread.join(5)
   self.assertFalse(thread.is_alive());self.assertEqual(office.job(job)['state'],'cancelled')
   self.assertTrue(errors);self.assertFalse(office.cancel_job(job))
 def test_assignment_collection_and_submission_routes_finish(self):
  motion=OfficeMotion();agents=[{'id':'a'}];homes={'a':(230,510)}
  work=[{'id':'job1','agent':'a','state':'working'}]
  start=motion.frame(agents,work,homes,now=0)['a'];self.assertTrue(start['moving'])
  seen=[]
  for i in range(1,200):seen.append(motion.frame(agents,work,homes,now=i*.1)['a']['position'])
  self.assertIn((500,230),seen);self.assertEqual(seen[-1],homes['a'])
  final=motion.frame(agents,work,homes,now=20)['a'];self.assertFalse(final['moving']);self.assertEqual(final['status'],'working')
  work[0]['state']='submitted'
  self.assertTrue(motion.frame(agents,work,homes,now=20.1)['a']['moving'])
  for i in range(202,410):final=motion.frame(agents,work,homes,now=i*.1)['a']
  self.assertFalse(final['moving']);self.assertEqual(final['position'],homes['a']);self.assertEqual(final['caption'],'Draft submitted')
 def test_reduced_motion_and_idle_check_do_not_loop(self):
  m=OfficeMotion();agents=[{'id':'a'}];homes={'a':(230,510)}
  self.assertFalse(m.frame(agents,[],homes,now=0)['a']['moving'])
  self.assertTrue(m.frame(agents,[],homes,now=1,checks={'a':1})['a']['moving'])
  final=m.frame(agents,[],homes,now=2,reduced=True,checks={'a':1})['a'];self.assertFalse(final['moving'])
  self.assertFalse(m.frame(agents,[],homes,now=3,checks={'a':1})['a']['moving'])
 def test_queue_check_is_local_and_recorded_without_creating_jobs(self):
  with tempfile.TemporaryDirectory() as folder:
   office=Office(folder);observer=OfficeObserver(office)
   observer.read(now=0);agents,state=observer.read(now=10)
   self.assertTrue(state['_checkins']);self.assertEqual(office.jobs(),[])
   before=len(office.recent_events());observer.read(now=11)
   self.assertEqual(len(office.recent_events()),before)
   self.assertIn('no assigned work',mind_text(office,{},state))
   job=office.create('Draft report');agent=agents[0]['id']
   with office.db() as db:
    db.execute("UPDATE jobs SET state='working' WHERE id=?",(job,))
    db.execute('INSERT INTO assignments VALUES(?,?,?,?,?,?)',('a1',job,agent,'Write intro','queued',''))
   self.assertEqual(office.check_in(agent)['task'],'Write intro')

if __name__=='__main__':unittest.main()
