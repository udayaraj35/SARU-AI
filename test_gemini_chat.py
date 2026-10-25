import unittest
from unittest.mock import Mock
from gemini_chat import generate,_working

class TextModelTests(unittest.TestCase):
 def setUp(self):_working.clear()
 def test_retired_model_uses_verified_stable_flash_once_and_caches_per_account(self):
  http=Mock();not_found=Mock(status_code=404);ok=Mock(status_code=200);ok.json.return_value={'candidates':[{'content':{'parts':[{'text':'hidden','thought':True},{'text':'Hello'}]}}]}
  http.post.side_effect=[not_found,ok,ok]
  http.get.return_value.json.return_value={'models':[{'name':'models/gemini-3.8-flash','supportedGenerationMethods':['generateContent']},{'name':'models/gemini-9.9-pro','supportedGenerationMethods':['generateContent']},{'name':'models/gemini-9.9-flash-preview','supportedGenerationMethods':['generateContent']}]}
  self.assertEqual(generate('synthetic','gemini-2.5-flash',{'contents':[]},http),('Hello','gemini-3.8-flash'))
  self.assertEqual(generate('synthetic','gemini-2.5-flash',{'contents':[]},http)[1],'gemini-3.8-flash');self.assertEqual(http.get.call_count,1);self.assertEqual(http.post.call_count,3)
 def test_quota_and_auth_never_retry_or_discover(self):
  for status in (401,403,429):
   http=Mock();http.post.return_value.status_code=status
   with self.assertRaises(ValueError):generate('synthetic','gemini-3.8-flash',{},http)
   http.get.assert_not_called();self.assertEqual(http.post.call_count,1)
 def test_no_available_replacement_never_claims_success(self):
  http=Mock();http.post.return_value.status_code=404;http.get.return_value.json.return_value={'models':[]}
  with self.assertRaises(ValueError):generate('synthetic','gemini-2.5-flash',{},http)
  self.assertEqual(http.post.call_count,1)

if __name__=='__main__':unittest.main()
