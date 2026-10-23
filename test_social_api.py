import unittest
from unittest.mock import Mock
from social_api import publish,SocialError
from update_manager import is_newer,configure_repository

class SocialTests(unittest.TestCase):
 def setUp(self):
  self.config={'meta_graph_version':'v25.0','whatsapp_phone_id':'123','facebook_page_id':'456','keys':{'WhatsApp Business':'secret','Facebook Page':'page-secret'}}
 def test_whatsapp_payload_and_acceptance(self):
  session=Mock();session.post.return_value.status_code=200;session.post.return_value.json.return_value={'messages':[{'id':'wamid.test'}]}
  self.assertEqual(publish('WhatsApp',self.config,'+359123456789','Hello',session),'wamid.test')
  args=session.post.call_args.kwargs
  self.assertEqual(args['json']['to'],'359123456789');self.assertFalse(args['allow_redirects'])
  self.assertNotIn('secret',session.post.call_args.args[0])
 def test_page_publishing(self):
  session=Mock();session.post.return_value.status_code=200;session.post.return_value.json.return_value={'id':'456_789'}
  self.assertEqual(publish('Facebook',self.config,'','Test post',session),'456_789')
  self.assertTrue(session.post.call_args.args[0].endswith('/456/feed'))
 def test_missing_credentials_never_calls(self):
  session=Mock();self.config['keys']={}
  with self.assertRaises(SocialError):publish('Facebook',self.config,'','Hello',session)
  session.post.assert_not_called()
 def test_error_never_exposes_token(self):
  session=Mock();session.post.return_value.status_code=403;session.post.return_value.json.return_value={'error':{'code':190,'message':'secret'}}
  with self.assertRaises(SocialError) as error:publish('Facebook',self.config,'','Hello',session)
  self.assertNotIn('secret',str(error.exception))
 def test_update_source_and_version(self):
  self.assertTrue(is_newer('v1.7.0','1.6.0'));self.assertFalse(is_newer('v1.6.0','1.6.0'))
  self.assertEqual(configure_repository('https://github.com/owner/saru'),'owner/saru')
  with self.assertRaises(ValueError):configure_repository('https://evil.example/a/b')

if __name__=='__main__':unittest.main()
