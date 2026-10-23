"""Best-effort secret-text exclusion. Use masked local fields, never voice, for secrets."""
import re
SECRET=re.compile(r'(?:\b(?:password|passcode|otp|one[ -]time code|bank pin|security code|api key)\s*(?:is|ho|:|=)\s*\S+|(?:पासवर्ड|पासकोड|ओटीपी)\s*[:=]?\s*\S+|\b(?:sk-[A-Za-z0-9_-]{20,}|AIza[A-Za-z0-9_-]{25,}))',re.I)
NOTICE='[Sensitive text withheld. Enter credentials only in the local masked field.]'
def contains_secret(text):return bool(SECRET.search(text or ''))
def safe_memory_text(text):return NOTICE if contains_secret(text) else text
