"""A per-utterance wake phrase, not speaker identity or biometric verification."""
import re

def addressed_to_saru(text):
 return bool(re.match(r'^\s*(?:(?:hey|hello|हे|हेलो)[,\s]+)?(?:saru|saaru|सारु|सारू|सरु)(?=$|[,!:।\s])',text,re.I))

def may_respond(text,required=True,typed=False):
 return not required or (addressed_to_saru(text) if text.strip() else bool(typed))
