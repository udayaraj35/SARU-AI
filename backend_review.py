"""Single-use, expiring grants bound to an exact backend operation."""
import hashlib
import json
import secrets
import threading
import time


def fingerprint(operation):
    return hashlib.sha256(json.dumps(operation,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()


class ReviewGate:
    def __init__(self):
        self.lock=threading.Lock();self.grants={}

    def grant(self,operation,seconds=120):
        token=secrets.token_urlsafe(32)
        with self.lock:
            now=time.monotonic()
            self.grants={k:v for k,v in self.grants.items() if v[1]>now}
            self.grants[token]=(fingerprint(operation),now+seconds)
        return token

    def consume(self,operation,token):
        with self.lock:entry=self.grants.pop(token,None)
        if not entry or entry[1]<time.monotonic() or not secrets.compare_digest(entry[0],fingerprint(operation)):
            raise PermissionError('This exact operation needs a fresh owner review.')


gate=ReviewGate()
