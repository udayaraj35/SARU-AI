"""A per-utterance wake phrase, not speaker identity or biometric verification."""
import re

def addressed_to_saru(text):
 return bool(re.match(r'^\s*(?:(?:hey|hello|हे|हेलो)[,\s]+)?(?:saru|saaru|सारु|सारू|सरु)(?=$|[,!:।\s])',text,re.I))

def may_respond(text,required=True,typed=False):
 return not required or (addressed_to_saru(text) if text.strip() else bool(typed))


def merge_transcript(current,fragment):
 """Handle cumulative transcripts and a split wake token without duplicating text."""
 if not fragment:return current
 if not current:return fragment
 if fragment.startswith(current):return fragment
 if current.endswith(fragment):return current
 if addressed_to_saru(current) and current.strip().casefold() in ('saru','saaru','सारु','सारू','सरु') and not fragment[0].isspace() and fragment[0] not in ',!:।':return current+' '+fragment
 return current+fragment
