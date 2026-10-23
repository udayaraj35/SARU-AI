"""Versioned atomic settings with Windows-user-bound DPAPI API secrets."""
import copy
import json
import os
from pathlib import Path

SCHEMA_VERSION = 2

class SettingsError(RuntimeError):
    pass

class WindowsProtector:
    def protect(self, value):
        if os.name != 'nt':
            raise SettingsError('Secret storage requires Windows DPAPI.')
        import win32crypt
        return win32crypt.CryptProtectData(value, 'SARU API keys', None, None, None, 1).hex()

    def unprotect(self, value):
        import win32crypt
        return win32crypt.CryptUnprotectData(bytes.fromhex(value), None, None, None, 1)[1]

class SettingsStore:
    def __init__(self, path, defaults, protector=None):
        self.path=Path(path)
        self.defaults=defaults
        self.protector=protector or WindowsProtector()

    def load(self):
        if not self.path.exists():
            return copy.deepcopy(self.defaults)
        try:
            raw=json.loads(self.path.read_text(encoding='utf-8-sig'))
            if not isinstance(raw,dict):raise ValueError('Settings must be an object')
            if int(raw.get('schema_version',1)) > SCHEMA_VERSION:
                raise SettingsError('Settings were created by a newer SARU version.')
            result=copy.deepcopy(self.defaults)
            result.update(raw)
            if 'protected_keys' in raw:
                result['keys']=json.loads(self.protector.unprotect(raw['protected_keys']).decode('utf8'))
            if not isinstance(result.get('keys'),dict):raise ValueError('Invalid key settings')
            result.pop('protected_keys',None)
            # Legacy plaintext is replaced only after protection succeeds.
            if raw.get('keys'):
                self.save(result)
            return result
        except SettingsError:
            raise
        except Exception as exc:
            raise SettingsError('Cannot read/decrypt settings. Original file preserved; restore it on the same Windows account or recover your backup.') from exc

    def save(self, settings):
        payload=copy.deepcopy(settings)
        keys=payload.pop('keys',{})
        payload['protected_keys']=self.protector.protect(json.dumps(keys).encode('utf8'))
        payload['schema_version']=SCHEMA_VERSION
        self.path.parent.mkdir(parents=True,exist_ok=True)
        temp=self.path.with_suffix('.tmp')
        try:
            with temp.open('w',encoding='utf8') as handle:
                json.dump(payload,handle,indent=2,ensure_ascii=False)
                handle.flush();os.fsync(handle.fileno())
            temp.replace(self.path)
        finally:
            temp.unlink(missing_ok=True)
