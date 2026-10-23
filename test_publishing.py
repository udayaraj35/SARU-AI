import json,sqlite3,tempfile,unittest
from pathlib import Path
from unittest.mock import Mock,patch
import requests
from content_workflow import PublishStore
from video_publishers import upload_video,trusted_upload
class ApprovalTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.video=self.root/'clip.mp4';self.video.write_bytes(b'video-fixture');self.store=PublishStore(self.root)
  self.identifier,self.post=self.store.create(self.video,'YouTube','My title','Caption','private',{'id':'channel1','name':'My channel','privacy':['private']},False,{})
 def tearDown(self):self.temp.cleanup()
 def test_no_upload_before_approval_and_no_duplicate(self):
  publisher=Mock(return_value={'id':'video1','state':'accepted','detail':'Processing'})
  with self.assertRaises(ValueError):self.store.publish(self.identifier,{},publisher)
  publisher.assert_not_called();self.store.approve(self.identifier);self.store.publish(self.identifier,{},publisher)
  with self.assertRaises(ValueError):self.store.publish(self.identifier,{},publisher)
  publisher.assert_called_once()
 def test_modified_video_rejected(self):
  self.store.approve(self.identifier);Path(self.post['path']).write_bytes(b'changed')
  publisher=Mock()
  with self.assertRaises(ValueError):self.store.publish(self.identifier,{},publisher)
  publisher.assert_not_called()
 def test_modified_caption_invalidates_approval(self):
  self.store.approve(self.identifier);self.post['description']='different'
  with self.store.connect() as con:con.execute('update drafts set payload=? where id=?',(json.dumps(self.post),self.identifier))
  with self.assertRaises(ValueError):self.store.publish(self.identifier,{},Mock())
 def test_unknown_network_state_never_retries(self):
  self.store.approve(self.identifier);publisher=Mock(side_effect=requests.Timeout('secret upload URL'))
  with self.assertRaises(requests.Timeout):self.store.publish(self.identifier,{},publisher)
  self.assertEqual(self.store.get(self.identifier)[1],'needs_check');self.assertNotIn('secret',str(self.store.get(self.identifier)[2]))
  with self.assertRaises(ValueError):self.store.publish(self.identifier,{},publisher)
  publisher.assert_called_once()
 def test_staging_is_separate_from_source(self):
  self.video.write_bytes(b'user edited original');self.store.approve(self.identifier)
  self.assertEqual(Path(self.post['path']).read_bytes(),b'video-fixture')
class UploadTests(unittest.TestCase):
 def response(self,body,code=200,headers=None):return Mock(status_code=code,json=Mock(return_value=body),headers=headers or {})
 def test_youtube_upload_uses_approved_metadata(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'clip.mp4';path.write_bytes(b'fixture')
   post={'path':str(path),'platform':'YouTube','destination_id':'abc','title':'Approved title','description':'Approved caption','privacy':'private','kids':False}
   session=Mock();session.get.return_value=self.response({'items':[{'id':'abc','snippet':{'title':'My channel'}}]})
   session.post.return_value=self.response({},headers={'Location':'https://www.googleapis.com/upload/test'})
   session.put.return_value=self.response({'id':'uploaded','status':{'privacyStatus':'private'}})
   with patch('video_publishers.youtube_token',return_value='token'):receipt=upload_video(post,{},session)
   self.assertEqual(receipt['id'],'uploaded');self.assertEqual(session.post.call_args.kwargs['json']['snippet']['title'],'Approved title');session.put.assert_called_once()
 def test_changed_account_prevents_upload(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'clip.mp4';path.write_bytes(b'fixture');session=Mock()
   post={'path':str(path),'platform':'YouTube','destination_id':'old','privacy':'private'}
   with patch('video_publishers.account_info',return_value={'id':'new','privacy':['private']}):
    with self.assertRaises(ValueError):upload_video(post,{},session)
   session.post.assert_not_called();session.put.assert_not_called()
 def test_facebook_video_uses_streaming_body(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'clip.mp4';path.write_bytes(b'fixture');session=Mock()
   session.get.return_value=self.response({'id':'123','name':'My page'});session.post.return_value=self.response({'id':'video123'})
   config={'meta_graph_version':'v25.0','facebook_page_id':'123','keys':{'Facebook Page':'secret'}}
   post={'path':str(path),'platform':'Facebook','destination_id':'123','privacy':'Page public','title':'Title','description':'Caption'}
   result=upload_video(post,config,session);self.assertEqual(result['id'],'video123')
   self.assertTrue(hasattr(session.post.call_args.kwargs['data'],'read'))
   self.assertNotIn('secret',session.post.call_args.args[0])
 def test_tiktok_upload_accepted_is_not_claimed_published(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'clip.mp4';path.write_bytes(b'fixture');session=Mock()
   creator={'creator_username':'me','creator_nickname':'My account','privacy_level_options':['SELF_ONLY'],'max_video_post_duration_sec':60}
   session.post.side_effect=[self.response({'data':creator,'error':{'code':'ok'}}),self.response({'data':{'publish_id':'ticket1','upload_url':'https://open-upload.tiktokapis.com/video/test'},'error':{'code':'ok'}})]
   session.put.return_value=self.response({})
   post={'path':str(path),'platform':'TikTok','destination_id':'me','privacy':'SELF_ONLY','title':'Title','description':'Caption','flags':dict.fromkeys(['disable_comment','disable_duet','disable_stitch','brand_content','brand_organic','is_aigc'],False)}
   with patch('video_creator.video_duration',return_value=3):result=upload_video(post,{'keys':{'TikTok':'secret'}},session)
   self.assertEqual(result['state'],'accepted');self.assertIn('confirmation',result['detail'])
   self.assertNotIn('Authorization',session.put.call_args.kwargs['headers'])
 def test_untrusted_upload_url_rejected(self):
  for url in ['http://www.googleapis.com/upload','https://evil.example/upload','https://open-upload.tiktokapis.com.evil.example/path','https://www.googleapis.com:8443/path']:
   with self.assertRaises(ValueError):trusted_upload(url,'YouTube')
if __name__=='__main__':unittest.main()
