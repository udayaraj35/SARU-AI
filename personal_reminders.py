"""Persistent local reminders; never claims alarms run while the PC sleeps/off."""
import datetime as dt
import re,sqlite3,time
from zoneinfo import ZoneInfo
ZONE=ZoneInfo('Europe/Sofia')


def reminder_intent(text,now=None):
 q=text.strip();low=q.casefold().rstrip('.!?।');now=time.time() if now is None else now
 if low in ('show reminders','my reminders','today tasks','aaja ko baki kam','आजको बाँकी काम'):return 'reminders',None
 m=re.fullmatch(r'(?:cancel reminder|complete reminder) (\d+)',low)
 if m:return 'reminder_cancel',int(m[1])
 m=re.fullmatch(r'(?:remind me in|reminder in) (\d+) (minutes?|hours?|days?) (?:to |: ?)(.+)',q,re.I)
 if m:
  seconds=int(m[1])*({'m':60,'h':3600,'d':86400}[m[2][0].lower()])
  if not 1<=seconds<=366*86400:return 'invalid','Reminder must be within one year.'
  return 'reminder_add',(now+seconds,m[3],'reminder')
 m=re.fullmatch(r'(?:malai )?(\d+) (minute|ghanta) (?:paxi|pachhi) (.+?) (?:samjhau|samjhaunu)',q,re.I)
 if m:
  seconds=int(m[1])*(60 if m[2].lower()=='minute' else 3600)
  if not 1<=seconds<=366*86400:return 'invalid','Reminder must be within one year.'
  return 'reminder_add',(now+seconds,m[3],'reminder')
 m=re.fullmatch(r'(alarm|reminder)(?: at)? (\d{1,2}):(\d{2})(?:\s*:\s*(.+))?',q,re.I)
 if m:
  hour,minute=int(m[2]),int(m[3])
  if hour>23 or minute>59:return 'invalid','Use a 24-hour time HH:MM.'
  local=dt.datetime.fromtimestamp(now,ZONE);target=local.replace(hour=hour,minute=minute,second=0,microsecond=0)
  if target.timestamp()<=now:target+=dt.timedelta(days=1)
  return 'reminder_add',(target.timestamp(),m[4] or 'Alarm',m[1].lower())
 if low.startswith(('remind me ','alarm ','reminder ')):return 'invalid','Say remind me in 10 minutes to call, or alarm 07:30: Wake up (Europe/Sofia).'
 return None,None

class ReminderStore:
 def __init__(self,path):
  self.db=sqlite3.connect(path);self.db.execute('CREATE TABLE IF NOT EXISTS reminders(id INTEGER PRIMARY KEY,due REAL,title TEXT,kind TEXT,state TEXT DEFAULT "pending")');self.db.commit()
 def add(self,due,title,kind='reminder'):
  if not isinstance(due,(int,float)) or not 0<due<1e12 or not title.strip() or len(title)>1000 or kind not in ('alarm','reminder'):raise ValueError('Invalid reminder')
  cursor=self.db.execute('INSERT INTO reminders(due,title,kind) VALUES(?,?,?)',(due,title.strip(),kind));self.db.commit();return cursor.lastrowid
 def pending(self):return self.db.execute('SELECT id,due,title,kind FROM reminders WHERE state="pending" ORDER BY due').fetchall()
 def due(self,now=None):return [row for row in self.pending() if row[1]<=(time.time() if now is None else now)]
 def outstanding(self):return self.db.execute('SELECT id,due,title,kind FROM reminders WHERE state IN ("pending","delivered") ORDER BY due').fetchall()
 def mark(self,identifier,state):
  if state not in ('delivered','cancelled'):raise ValueError('Invalid reminder state')
  changed=self.db.execute('UPDATE reminders SET state=? WHERE id=? AND state IN ("pending","delivered")',(state,identifier)).rowcount;self.db.commit();return bool(changed)
 def close(self):self.db.close()


def format_due(timestamp):return dt.datetime.fromtimestamp(timestamp,ZONE).strftime('%Y-%m-%d %H:%M %Z')
