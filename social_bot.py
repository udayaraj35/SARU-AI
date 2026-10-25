"""Visible Playwright social sessions and exact reviewed submissions.

Site DOMs change. Missing/ambiguous controls fail closed; submission is never
reported as delivery. QR, passwords, 2FA and CAPTCHA remain with the account user.
"""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import re
import threading
import uuid
from urllib.parse import urlencode,urlsplit
from backend_review import gate,fingerprint
from secret_handling import contains_secret,safe_memory_text

SITES={'whatsapp':'https://web.whatsapp.com','facebook':'https://www.facebook.com','instagram':'https://www.instagram.com','x':'https://x.com'}


def file_record(path):
    value=Path(path).resolve()
    if not value.is_file() or value.stat().st_size>100*1024*1024:raise ValueError('Attachment must be an existing file under 100 MiB')
    return {'path':str(value),'sha256':hashlib.sha256(value.read_bytes()).hexdigest()}


class SocialBot:
    def __init__(self,data,stealth=False):
        self.root=Path(data)/'social_sessions';self.root.mkdir(parents=True,exist_ok=True)
        self.executor=ThreadPoolExecutor(max_workers=1,thread_name_prefix='saru-social')
        self.stealth=stealth;self.playwright=None;self.contexts={};self.previews={}

    def submit(self,method,*args,**kwargs):
        return self.executor.submit(getattr(self,method),*args,**kwargs)

    def _page(self,platform):
        if platform not in SITES:raise ValueError('Use whatsapp, facebook, instagram or x')
        if self.playwright is None:
            # Reuse SARU's separate reviewed Chromium download; never user's Chrome profile.
            data=self.root.parent
            browsers=data/'advanced/browsers'
            if browsers.is_dir():os.environ.setdefault('PLAYWRIGHT_BROWSERS_PATH',str(browsers))
            from playwright.sync_api import sync_playwright
            self.playwright=sync_playwright().start()
        context=self.contexts.get(platform)
        if context is None:
            context=self.playwright.chromium.launch_persistent_context(str(self.root/platform),headless=False,accept_downloads=False,viewport={'width':1150,'height':800})
            if self.stealth:
                from playwright_stealth import Stealth
                Stealth().apply_stealth_sync(context)
            self.contexts[platform]=context
        try:page=context.pages[0] if context.pages else context.new_page()
        except Exception:
            self.contexts.pop(platform,None);raise RuntimeError('Social browser closed; open the session again')
        page.bring_to_front();return page

    @staticmethod
    def _one(locator,what):
        if locator.count()!=1:raise ValueError('Expected one '+what+'; inspect the logged-in page and select the correct account/target')
        if not locator.is_visible():raise ValueError(what+' is not visible')
        return locator

    @staticmethod
    def _origin(page,platform):
        expected=urlsplit(SITES[platform]).hostname
        if urlsplit(page.url).scheme!='https' or urlsplit(page.url).hostname not in (expected,expected.removeprefix('www.')):raise ValueError('Social page left the expected HTTPS platform')

    def open(self,platform):
        page=self._page(platform);page.goto(SITES[platform],wait_until='domcontentloaded',timeout=45000)
        return 'Opened '+platform+' session. Complete login/QR locally if needed.'

    def open_profile(self,platform,url):
        parsed=urlsplit(url);expected=urlsplit(SITES[platform]).hostname
        if parsed.scheme!='https' or parsed.hostname not in (expected,expected.removeprefix('www.')) or parsed.username or parsed.password:raise ValueError('Use a profile URL on the selected platform')
        page=self._page(platform);page.goto(url,wait_until='domcontentloaded',timeout=45000)
        return 'Profile opened in the local social session: '+page.url

    def _upload(self,page,files):
        """Require one compatible file input; never guess a hidden upload target."""
        inputs=page.locator('input[type="file"]');candidates=[]
        for value in inputs.all():
            accept=(value.get_attribute('accept') or '').casefold()
            if not accept or '*'==accept or all(Path(r['path']).suffix.lower() in accept or ('image/' in accept and Path(r['path']).suffix.lower() in ('.png','.jpg','.jpeg','.webp','.gif')) or ('video/' in accept and Path(r['path']).suffix.lower() in ('.mp4','.mov','.webm')) for r in files):candidates.append(value)
        if len(candidates)!=1:raise ValueError('Attachment input is ambiguous. Choose the correct upload type in the visible account first.')
        candidates[0].set_input_files([r['path'] for r in files])

    def unread(self):
        page=self._page('whatsapp')
        if urlsplit(page.url).hostname!='web.whatsapp.com':page.goto(SITES['whatsapp'],wait_until='domcontentloaded')
        page.locator('#pane-side').wait_for(state='visible',timeout=15000)
        rows=page.locator('#pane-side [role="row"]').all()
        result=[]
        for row in rows:
            if row.locator('[aria-label*="unread" i]').count():result.append(safe_memory_text(row.inner_text())[:1200])
            if len(result)>=50:break
        return {'unread_visible_chats':result,'scope':'currently loaded chat list only; not a complete account export'}

    def read_chat(self,target):
        page=self._whatsapp_target(target)
        return {'target':target,'visible_messages':[safe_memory_text(x.inner_text())[:2000] for x in page.locator('#main .message-in, #main .message-out').all()[-30:]],'scope':'loaded visible messages only'}

    def _whatsapp_target(self,target):
        page=self._page('whatsapp')
        if re.fullmatch(r'\+?[1-9]\d{6,14}',target):
            page.goto(SITES['whatsapp']+'/send?'+urlencode({'phone':target.lstrip('+')}),wait_until='domcontentloaded',timeout=45000)
        else:
            if urlsplit(page.url).hostname!='web.whatsapp.com':page.goto(SITES['whatsapp'],wait_until='domcontentloaded')
            page.locator('#pane-side').wait_for(state='visible',timeout=15000)
            self._one(page.locator('#pane-side').get_by_title(target,exact=True),'exact WhatsApp contact').click()
        page.locator('#main header').wait_for(state='visible',timeout=20000)
        self._origin(page,'whatsapp')
        if not re.fullmatch(r'\+?[1-9]\d{6,14}',target):
            self._one(page.locator('#main header').get_by_title(target,exact=True),'recipient header')
        return page

    def prepare(self,operation):
        platform=operation['platform'];action=operation.get('action','post');text=operation.get('text','')
        if contains_secret(text):raise ValueError('Credentials must not be posted or saved in drafts')
        if len(text)>10000:raise ValueError('Social text limit is 10,000 characters')
        files=[file_record(p) for p in operation.get('files',[])]
        if len(files)>4:raise ValueError('At most four attachments per reviewed submission')
        page=self._page(platform);submit=None;editor=None;header=''
        if platform=='whatsapp':
            if action!='send':raise ValueError('WhatsApp action must be send')
            page=self._whatsapp_target(operation['target'])
            header=page.locator('#main header').inner_text()
            editor=self._one(page.locator('#main footer [contenteditable="true"][role="textbox"]'),'WhatsApp composer')
            editor.fill(text)
            if files:
                attach=page.locator('#main footer').get_by_role('button',name=re.compile('Attach',re.I))
                self._one(attach,'attachment control').click()
                self._upload(page,files)
                # The attachment preview has its own caption and final Send button.
                preview=page.locator('[role="dialog"]').filter(has=page.locator('[contenteditable="true"]'))
                preview=self._one(preview,'WhatsApp attachment preview')
                editor=self._one(preview.locator('[contenteditable="true"]'),'attachment caption')
                editor.fill(text)
                submit=preview.get_by_role('button',name=re.compile('^Send$',re.I))
            else:submit=page.locator('#main footer button:has([data-icon="send"]), #main footer [role="button"]:has([data-icon="send"])')
        elif action in ('like','comment'):
            target=operation['target'];parsed=urlsplit(target)
            expected=urlsplit(SITES[platform]).hostname
            if parsed.scheme!='https' or parsed.hostname not in (expected,expected.removeprefix('www.')) or parsed.username or parsed.password:raise ValueError('Use an exact HTTPS post URL on the selected platform')
            page.goto(target,wait_until='domcontentloaded',timeout=45000)
            self._origin(page,platform)
            if action=='comment':
                editor=page.get_by_role('textbox',name=re.compile('comment|reply',re.I));self._one(editor,'comment editor').fill(text)
                submit=page.get_by_role('button',name=re.compile('^(Post|Reply|Comment)$',re.I))
            else:submit=page.get_by_role('button',name=re.compile('^Like$',re.I))
        elif platform=='x':
            page.goto(SITES[platform]+'/compose/post',wait_until='domcontentloaded',timeout=45000)
            self._origin(page,platform)
            editor=self._one(page.locator('[data-testid="tweetTextarea_0"]'),'X composer');editor.fill(text)
            if files:page.locator('input[type="file"]').set_input_files([r['path'] for r in files])
            submit=page.locator('[data-testid="tweetButton"]')
        elif platform=='facebook':
            page.goto(SITES[platform],wait_until='domcontentloaded',timeout=45000)
            self._origin(page,platform)
            trigger=page.get_by_role('button',name=re.compile("What's on your mind",re.I));self._one(trigger,'Facebook create post').click()
            dialog=self._one(page.get_by_role('dialog'),'Facebook post dialog')
            editor=self._one(dialog.get_by_role('textbox'),'Facebook post editor');editor.fill(text)
            if files:
                self._one(dialog.get_by_role('button',name=re.compile('Photo/video',re.I)),'Facebook media attachment').click()
                self._upload(dialog,files)
            submit=dialog.get_by_role('button',name='Post',exact=True)
        elif platform=='instagram':
            if not files:raise ValueError('Instagram posts require an image or video attachment')
            page.goto(SITES[platform],wait_until='domcontentloaded',timeout=45000)
            self._origin(page,platform)
            create=page.get_by_role('link',name=re.compile('^New post$|^Create$',re.I))
            self._one(create,'Instagram create post').click()
            self._upload(page,files)
            # Instagram's crop and filter steps each have a distinct Next control.
            for _ in range(2):
                next_button=page.get_by_role('button',name='Next',exact=True)
                self._one(next_button,'Instagram Next').click()
            editor=self._one(page.get_by_role('textbox',name=re.compile('caption',re.I)),'Instagram caption')
            editor.fill(text);submit=page.get_by_role('button',name='Share',exact=True)
        else:raise ValueError('Unsupported social operation')
        self._one(submit,'final submit control')
        identifier=uuid.uuid4().hex
        review={**operation,'files':files,'url':page.url,'recipient_header':header,'preview_id':identifier}
        self.previews[identifier]={'review':review,'page':page,'editor':editor,'submit':submit,'digest':fingerprint(review)}
        preview=self.root/'previews';preview.mkdir(exist_ok=True)
        page.screenshot(path=str(preview/(identifier+'.png')))
        return review

    def commit(self,review,token):
        gate.consume(review,token)
        saved=self.previews.pop(review['preview_id'],None)
        if not saved or fingerprint(review)!=saved['digest']:raise ValueError('Social preview expired or changed')
        page=saved['page']
        if page.is_closed() or page.url!=review['url']:raise ValueError('Page changed since review')
        self._origin(page,review['platform'])
        for record in review['files']:
            if file_record(record['path'])!=record:raise ValueError('Attachment changed since review')
        if review['platform']=='whatsapp' and page.locator('#main header').inner_text()!=review['recipient_header']:raise ValueError('Recipient changed since review')
        editor=saved['editor']
        if editor is not None and editor.inner_text().strip()!=review.get('text','').strip():raise ValueError('Draft changed since review')
        button=self._one(saved['submit'],'reviewed final submit control')
        if not button.is_enabled():raise ValueError('Submit control is disabled')
        # One attempt only. Network ambiguity must never trigger a duplicate send.
        try:button.click(timeout=10000)
        except Exception:raise RuntimeError('Submission result unknown. Inspect the account before retrying.') from None
        return {'state':'submitted_unconfirmed','platform':review['platform'],'target':review.get('target','current account'),'detail':'Final control clicked once. Delivery/publication must be checked in the account.'}

    def close(self):
        for context in self.contexts.values():
            try:context.close()
            except Exception:pass
        self.contexts.clear();self.previews.clear()
        if self.playwright:self.playwright.stop();self.playwright=None
