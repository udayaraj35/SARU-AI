"""Voice intent gate: completed owner requests, never assistant-generated actions."""
import re
from assistant_commands import parse_command,normalize_request
from launch_intents import normalize_launch


def voice_request(text):
 from action_consent import pending_actions,consent_reply
 if pending_actions.peek() and consent_reply(text) is not None:return 'pending_reply',consent_reply(text)
 action,arg=parse_command(text)
 if action in ('backend','desktop_input','wacrm_panel','wacrm_read','wacrm_send','media_control','media_search','media_play','media_save','youtube_search'):return action,arg
 wake=bool(re.match(r'^\s*(?:hey\s+)?(?:saru|सारु|सरु)[,!:।\s]+',text,re.I))
 normalized=normalize_launch(normalize_request(text))
 explicit=bool(re.search(r'^(?:open|launch|play|pause|stop|save|set|take|capture|show|view|search|remember|improve|update|change your code|create|make|mute|lock|volume\s+\d|brightness\s+\d)|(?:kholnu|kholideu|kholidinu|khola|gara|garnu|banaideu|बनाऊ|बनाइदेऊ|खोल्नु|खोलिदेऊ|खोलिदेउ|चलाऊ|बजाऊ|देखाऊ|गर)\s*[.!?।]*$',normalized,re.I))
 if action and (wake or explicit or action in ('outbox_add','outbox_list','outbox_cancel','ui_control','document_editor','camera','camera_ask','voice_profiles','voice_enroll','voice_compare','reminder_add','reminder_cancel','reminders','power','self_improve','repo_add','repo_center','office','office_status','desktop_task','saru_control','select_app')):return action,arg
 return None,None


def feature_request(text):
 """Offer a proposal only for a concrete missing action, not casual chat."""
 q=normalize_request(text)
 return bool(re.match(r'^(?:build|create|make|add|automate|install|change|update|improve)\s+\S',q,re.I) or re.search(r'\S.+\s+(?:banaideu|banau|thapnu|बनाइदेऊ|बनाऊ|थप)\s*[.!?।]*$',q,re.I))
