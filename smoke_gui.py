"""Local GUI smoke test. Uses isolated data, no microphone/API/repair actions."""
import os
from pathlib import Path
import tempfile
import tkinter as tk

base=Path(__file__).resolve().parent
os.chdir(base)
with tempfile.TemporaryDirectory(prefix='.gui-test-',dir=base) as temp:
 os.environ['SARU_DATA_DIR']=temp
 os.environ['SARU_DISABLE_AUTOLISTEN']='1'
 original=tk.Misc.mainloop
 def smoke(root,*args,**kwargs):
  import inspect
  app=inspect.currentframe().f_back.f_globals
  app['cfg']['work_folder']=str(Path(temp)/'Work')
  try:
   root.update_idletasks();root.update()
   assert app['active_page'].__class__.__name__=='Dashboard'
   assert app['boot'].progress.ready() and app['boot'].closed
   assert root.state()!='withdrawn'
   assert len(app['active_page'].command.get())==0
   from unittest.mock import Mock,patch
   route=Mock()
   with patch.dict(app,{'run_agent_task':route}),patch.object(app['voice_hub'],'send_text') as cloud:
    app['send_message']('एप खोल्नुहोस्',app['active_page'].chat_output)
    route.assert_called_once_with('एप खोल्नुहोस्',app['active_page'].chat_output);cloud.assert_not_called()
   app['cfg']['speak']=False
   page=app['active_page']
   page.render({'internet_online':False,'internet_detail':'Internet not reachable','adapters':['Wi-Fi']});assert page.online.cget('text')=='● Offline' and page.online.cget('fg')=='#ff3b30'
   page.render({'internet_online':True,'internet_detail':'Internet connection verified'});assert page.online.cget('text')=='● Online' and page.online.cget('fg')=='#00e676'
   with patch.object(app['voice_hub'],'speak_reply',return_value=True) as feedback:
    app['announce_local']('Local command result for GUI test');feedback.assert_called_once_with('Local command result for GUI test')
   app['cfg']['speak']=True
   with patch.object(app['voice_hub'],'engine',Mock(active=True)),patch.object(app['voice_hub'],'speak_reply',return_value=True) as feedback,patch.dict(app,{'speak':Mock()}) as patched:
    app['speak_ai_reply']('Completed chat answer');feedback.assert_called_once_with('Completed chat answer');patched['speak'].assert_not_called()
   app['cfg']['speak']=False
   # Own-app commands remain local, and planning does not request owner verification.
   app['remember_message']('Boss','Synthetic saffron preference')
   app['remember_note']('Synthetic note','Tea without sugar')
   app['announce_local']('Synthetic task completed')
   app['memory_center']();root.update_idletasks();memory_page=app['active_page']
   assert memory_page.__class__.__name__=='MemoryPanel'
   memory_page.query.set('saffron');memory_page.refresh();assert 'Synthetic saffron preference' in memory_page.output.get('1.0','end')
   memory_page.query.set('');memory_page.kind.set('task');memory_page.refresh();assert 'Synthetic task completed' in memory_page.output.get('1.0','end')
   app['back_home']()
   app['advanced_center']();root.update_idletasks()
   assert app['active_page'].__class__.__name__=='AdvancedPanel'
   assert 'BUNDLED ACTIONS' in app['active_page'].details.get('1.0','end')
   app['back_home']()
   with patch.dict(app,{'authorize_source_edit':Mock(return_value=False)}):
    studio=app['improvement_studio']('fix voice interruptions');root.update_idletasks()
    assert studio.winfo_exists()
    chosen=[studio.files.get(i) for i in studio.files.curselection()]
    assert 'live_voice.py' in chosen and 'dashboard_layout.py' not in chosen
    app['send_message']('saru update status');assert app['pending_actions'].peek() is None
    with patch('improvement_ui.generate') as generation:
     app['send_message']('generate saru update')
     assert app['pending_actions'].peek() is not None
     app['process_pending_reply']('cancel');generation.assert_not_called()
    studio.set_request('change interface colors')
    assert 'dashboard_layout.py' in [studio.files.get(i) for i in studio.files.curselection()]
    studio.close()
   app['send_message']('open settings');root.update_idletasks()
   app['send_message']('close settings');root.update_idletasks()
   assert app['active_page'].__class__.__name__=='Dashboard'
   power=Mock(return_value='Mock power requested')
   with patch.dict(app,{'propose_power_action':power}):
    app['send_message']('pc off gara');power.assert_called_once_with('shutdown')
    assert app['pending_actions'].peek() is None
   with patch.dict(app,{'launch_named_application':Mock()}):
    app['send_message']('open Google Chrome');assert app['pending_actions'].peek() is None
   with patch.dict(app,{'media_player':Mock()}) as mocked:
    app['send_message']('open YouTube');assert app['pending_actions'].peek() is None;mocked['media_player'].assert_called_once()
   from ui_control import UiControl
   app['send_message']('list buttons');assert 'Available buttons' in app['status'].get()
   invoked=Mock();test_button=tk.Button(root,text='Test exact SARU button',command=invoked);test_button.place(x=300,y=100);root.update_idletasks()
   app['send_message']('press button Test exact SARU button');invoked.assert_called_once()
   assert app['pending_actions'].peek() is None
   test_button.configure(state='disabled');app['send_message']('press button Test exact SARU button');assert invoked.call_count==1
   test_button.destroy()
   app['send_message']('open option Settings');assert app['active_page'].__class__.__name__=='SettingsPanel'
   app['send_message']('select tab Voice')
   assert app['active_page'].book.tab(app['active_page'].book.select(),'text')=='Voice'
   app['send_message']('set option new_key to forbidden');assert app['pending_actions'].peek() is None
   app['back_home']()
   from screen_corners import ScreenCorners
   corners=ScreenCorners(root,app['cfg']);corners.show();root.update_idletasks()
   assert len(corners.windows)==4
   assert all(window.winfo_exists() for window,canvas in corners.windows)
   from theme_manager import palette
   assert corners.windows[0][1].itemcget(1,'fill')==palette(app['cfg'].get('theme'))['primary']
   corners.close();assert corners.closed
   from document_editor_ui import DocumentEditor
   editor=DocumentEditor(root,app['offer_pending_action'],app['announce_local']);root.update_idletasks()
   assert editor.old.get()=='';editor.destroy()
   from PIL import Image
   with patch('camera_companion.CameraCompanion.capture'),patch('camera_companion.describe_frame') as vision:
    app['personal_hub'].handle('camera','open');camera=app['personal_hub'].camera
    camera.frame=Image.new('RGB',(16,16));camera.frame_at=__import__('time').monotonic()
    app['cfg'].setdefault('keys',{})['Gemini']='test-only-camera-key'
    camera.analyze();assert app['pending_actions'].peek() is not None
    app['process_pending_reply']('cancel');vision.assert_not_called()
    app['personal_hub'].handle('camera','stop');assert camera.closed
   app['personal_hub'].handle('voice_profiles');assert app['personal_hub'].voices.winfo_exists()
   app['personal_hub'].voices.destroy()
   app['send_message']('remind me in 10 minutes to GUI test task')
   assert not app['personal_hub'].reminders.pending()
   app['process_pending_reply']('ok');assert len(app['personal_hub'].reminders.pending())==1
   old_theme=app['cfg'].get('theme')
   app['send_message']('theme blue')
   assert app['pending_actions'].peek() is None
   assert app['cfg']['theme']=='Ocean Cyan'
   assert app['pending_actions'].peek() is None
   app['send_message']('theme pink')
   assert app['cfg']['theme']=='Neon Rose'
   assert app['pending_actions'].peek() is None
   page=app['active_page'];root.update_idletasks()
   assert len(page.nav_buttons)==11
   assert not page.details_open
   assert hasattr(page,'header_status')
   assert page.online.master.master is page.nav
   assert page.header_status.clock.grid_info()['column']==1
   assert page.header_status.weather.grid_info()['column']==0
   page.header_status.clock.event_generate('<Button-1>');root.update_idletasks()
   assert app['active_page'].__class__.__name__=='SettingsPanel'
   assert app['active_page'].book.tab(app['active_page'].book.select(),'text')=='Appearance'
   assert len(app['active_page'].country_picker.cget('values'))>200
   picker=app['active_page'].country_picker
   assert picker.winfo_rooty()+picker.winfo_height()<root.winfo_rooty()+root.winfo_height()-60
   app['back_home']();page=app['active_page']
   assert page.control_panel.master is page.body
   assert page.panels[3].master is page.body
   assert page.home_view=='assistant' and page.panels[0].winfo_manager()=='grid'
   page.toggle_workspace();root.update_idletasks();assert page.home_view=='office' and not page.panels[0].winfo_manager()
   page.refresh_office_preview()
   assert page.office_preview.find_withtag('mind')
   assert page.office_preview.find_withtag('memory')
   page.toggle_workspace();root.update_idletasks();assert page.home_view=='assistant' and app['cfg']['home_view']=='assistant'
   assert not page.control_panel.winfo_manager()
   page.toggle_details();root.update_idletasks();assert page.control_panel.winfo_manager()=='grid'
   page.toggle_details();root.update_idletasks();assert not page.control_panel.winfo_manager()
   assert len(page.hero_buttons)==5 and len(page.hero_voice_buttons)==4
   assert page.holo_renderer is not None and len(page.scene_buttons)==3
   page.scene_buttons[0].invoke();assert page.drawer_open
   page.scene_buttons[1].invoke();root.update_idletasks();assert page.control_panel.winfo_manager()=='grid'
   page.scene_buttons[1].invoke();root.update_idletasks();assert not page.control_panel.winfo_manager()
   with patch.dict(page.actions,{'Saved memory':Mock()}) as hologram_actions:
    from types import SimpleNamespace
    left,top,right,bottom=page.holo_renderer.sphere_bounds
    page.hologram_click(SimpleNamespace(x=(left+right)/2,y=(top+bottom)/2));hologram_actions['Saved memory'].assert_called_once_with()
   page.scene_buttons[2].invoke();root.update_idletasks();assert app['active_page'].__class__.__name__=='SettingsPanel'
   app['back_home']();page=app['active_page']
   assert 'battery' in page.gauges
   assert page.panels[4].master is page.body
   assert any('Social Media' in name for name in app['active_page'].nav_buttons)
   assert app['active_page'].settings_button.pack_info()['side']=='bottom'
   assert hasattr(app['active_page'],'chat_output')
   app['chat_window']();assert not any(isinstance(w,tk.Toplevel) for w in root.winfo_children() if w is not app['orb'])
   assert len(app['active_page'].scales)==3
   app['active_page'].provider_var.set('OpenAI');app['active_page'].select_provider();assert app['cfg']['provider']=='OpenAI'
   app['active_page'].provider_var.set('Gemini');app['active_page'].select_provider()
   previous=app['cfg']['photo'];app['cfg']['photo']='Z:/missing-old-install/portrait.png';app['show_dashboard']();assert app['active_page'].holo_renderer is not None;app['orb'].reload();assert app['orb'].photo is not None
   app['cfg']['dashboard_style']='Portrait';app['show_dashboard']();assert hasattr(app['active_page'],'avatar')
   app['cfg']['photo']=previous;app['cfg']['dashboard_style']='Holographic';app['show_dashboard']()
   companion=app['orb'];assert companion.__class__.__name__=='FloatingCompanion'
   for state in ('LISTENING','SPEAKING','MUTED','STOPPED'):companion.set_state(state,.4);root.update_idletasks()
   companion.reload();assert companion.canvas.find_all()
   companion.toggle_controls();root.update_idletasks()
   assert companion.controls.state()!='withdrawn'
   assert set(companion.device_controls.sliders)=={'volume','brightness'}
   from tkinter import ttk
   from theme_manager import THEMES,apply_theme
   for theme,colors in THEMES.items():
    app['cfg']['theme']=theme;apply_theme(root,theme);root.update_idletasks()
    assert companion.controls.cget('bg')==colors['bg']
    assert ttk.Style(root).lookup('TCombobox','fieldbackground',('readonly',))==colors['field']
    assert ttk.Style(root).lookup('TCombobox','foreground',('readonly',))==colors['text']
   companion.toggle_controls();assert companion.controls.state()=='withdrawn'
   app['companion_screen']();root.update_idletasks()
   screen_window=next(w for w in root.winfo_children() if isinstance(w,tk.Toplevel) and w is not companion)
   assert screen_window.winfo_children()[0].__class__.__name__=='ScreenPanel'
   screen_window.destroy()
   app['settings']();panel=app['active_page']
   assert len(panel.book.tabs())==8
   for tab in panel.book.tabs():panel.book.select(tab);root.update_idletasks();root.update()
   original_size=app['cfg']['voice_rate'];panel.fields['voice_rate'].set('bad');panel.commit();assert app['cfg']['voice_rate']==original_size
   panel.fields['voice_rate'].set(str(original_size));panel.fields['new_key'].set('synthetic-key-only');panel.commit()
   panel.fields['display_country'].set('Nepal (NP)');root.update_idletasks()
   assert tuple(panel.timezone_picker.cget('values'))==('Asia/Kathmandu',)
   panel.commit();assert app['cfg']['display_country']=='NP' and app['cfg']['display_timezone']=='Asia/Kathmandu'
   panel.fields['display_country'].set('United States (US)');root.update_idletasks()
   assert len(panel.timezone_picker.cget('values'))>1
   panel.fields['display_timezone'].set('America/New_York');panel.commit();assert app['cfg']['display_timezone']=='America/New_York'
   assert 'synthetic-key-only' not in Path(temp,'settings.json').read_text(encoding='utf8')
   app['back_home']()
   page=app['active_page'];root.update_idletasks()
   assert page.online.winfo_rooty()>page.nav.winfo_rooty()
   assert page.header_status.clock.winfo_rootx()>page.header_status.weather.winfo_rootx()
   app['office_center']('Prepare a PDF report');office=app['active_page'];root.update_idletasks()
   assert office.__class__.__name__=='OfficePanel'
   assert len(office.office.agents())==4
   assert office.format.get()=='pdf'
   assert office.canvas.find_all()
   assert office.canvas.find_withtag('saru_desk')
   office.toggle_desk();root.update_idletasks();assert not office.desk_open
   office.open_team();root.update_idletasks();assert office.desk_open
   commands=len(office.canvas._tclCommands or [])
   for index in range(20):office.draw()
   assert len(office.canvas._tclCommands or [])==commands
   app['back_home']()
   app['profile_page']();profile=app['active_page'];root.update_idletasks()
   assert len(profile.book.tabs())==2
   assert profile.fields['creator']['name'].get()=='Udaya Raj Khanal'
   assert profile.fields['creator']['youtube'].get()=='https://www.youtube.com/@udayaraj3'
   assert 'creator' in profile.images
   profile.fields['owner']['name'].set('GUI Test Owner');profile.commit();assert app['cfg']['owner_name']=='GUI Test Owner'
   app['back_home']()
   app['repository_center']();root.update_idletasks()
   repo_window=next(child for child in root.winfo_children() if child.__class__.__name__=='RepoCenter');repo_window.close()
   from app_picker import AppPicker
   picker=AppPicker(root,app['cfg'],app['save'],app['screen_control']);root.update_idletasks();picker.close()
   for name in ('settings','profile_page','appearance_center','autonomous_console','agent_center','chat_window','screen_control','social_media_page'):
    app[name]();root.update_idletasks()
    assert app['active_page'].winfo_exists()
    app['back_home']();root.update_idletasks()
    assert app['active_page'].__class__.__name__=='Dashboard'
   app['chat_window']()
   root.geometry('1400x1000');root.update();sidebar=app['active_page']
   assert sidebar.sidebar_links.winfo_height()<=sidebar.navcanvas.winfo_height(),(sidebar.sidebar_links.winfo_height(),sidebar.navcanvas.winfo_height(),sidebar.sidebar_navigation.height,[(b.cget('height'),b.cget('font')) for b in sidebar.sidebar_navigation.buttons],root.geometry())
   for width,height in ((890,570),(1280,790),(1600,900)):
    root.geometry(f'{width}x{height}');app['active_page'].focus_chat();root.update()
    assert app['active_page'].command.winfo_width()>100
    assert app['active_page'].chat_output.winfo_height()>30
    assert app['active_page'].command.winfo_height()>15
    assert app['active_page'].dock_side=='right'
    assert app['active_page'].chat_dock.winfo_x()>app['active_page'].nav.winfo_x()+app['active_page'].nav.winfo_width()
    assert app['active_page'].chat_dock.winfo_y()+app['active_page'].chat_dock.winfo_height()<=app['active_page'].composer.winfo_y(),(width,height,app['active_page'].chat_dock.winfo_geometry(),app['active_page'].composer.winfo_geometry())
    page=app['active_page'];app['inline_control']('brightness');assert app['active_page'] is page
    if height==570:
     page.workspace_button.event_generate('<MouseWheel>',delta=-120);root.update()
     assert page.navcanvas.yview()[0]>0,(page.navcanvas.yview(),page.sidebar_links.winfo_height(),page.navcanvas.winfo_height(),page.navcanvas.cget('scrollregion'),page.workspace_button.bind('<MouseWheel>'))
   root.geometry('1280x790');root.update_idletasks();assert app['active_page'].dock_side=='right'
   from theme_manager import THEMES,apply_theme
   for theme,palette in THEMES.items():
    app['cfg']['theme']=theme;apply_theme(app['active_page'],theme);root.update_idletasks()
    assert app['active_page'].cget('bg')==palette['bg']
    assert app['active_page'].settings_button.theme_palette==palette
   app['toggle_fullscreen']();root.update_idletasks();assert bool(root.attributes('-fullscreen'))
   app['leave_fullscreen']();root.update_idletasks();assert not bool(root.attributes('-fullscreen'))
   from queue import Queue
   from types import SimpleNamespace
   page=app['active_page'];page.controls.close()
   class FakeControls:
    def __init__(self):self.events=Queue();self.serial=0;self.calls=[]
    def set(self,name,value):
     self.serial+=1;self.calls.append((name,value));self.events.put((name,self.serial,{name:value},None));return self.serial
    def close(self):pass
   page.controls=FakeControls();page.render({'volume':45})
   scale=page.scales['volume'];left=scale.coords(0)[0];right=scale.coords(100)[0]
   page.drag_slider('volume',SimpleNamespace(x=left+(right-left)*.7),True)
   target=scale.get();assert 69<=target<=71
   page.render({'volume':20});assert scale.get()==target
   page.release_slider('volume',SimpleNamespace(x=left+(right-left)*.8));page.poll_controls()
   assert 79<=page.controls.calls[-1][1]<=81
   assert 'volume' not in page.control_versions
   assert abs(scale.get()-80)<=1
   page.chat_output.delete('1.0','end');page.voice_event('transcript',('SARU','Hello '));page.voice_event('transcript',('SARU','world'));page.voice_event('conversation_turn',('',''))
   assert page.chat_output.get('1.0','end').count('SARU:')==1
   # Closing keeps the rest of this assistant turn hidden. New owner speech
   # reopens it; idle hiding preserves all transcript history.
   saved=page.chat_output.get('1.0','end');page.hide_chat();root.update_idletasks()
   assert not page.drawer_open and not page.chat_dock.winfo_manager()
   page.voice_event('transcript',('SARU','More of the same reply'));assert not page.drawer_open
   page.voice_event('transcript',('You','New owner request'));root.update_idletasks();assert page.drawer_open
   page.voice_event('conversation_turn',('',''));page.hero_voice_state='LISTENING'
   page.command.delete(0,'end');page.winfo_pointerxy=lambda:(-10000,-10000)
   page.cancel_chat_idle();page.chat_idle();root.update_idletasks();assert not page.drawer_open
   assert saved.strip() in page.chat_output.get('1.0','end')
   app['run_agent_task']('chat open gara',quiet=True);root.update_idletasks();assert page.drawer_open
   app['run_agent_task']('chat banda gara',quiet=True);root.update_idletasks();assert not page.drawer_open
   page.toggle_chat();root.update_idletasks();assert page.drawer_open and page.dock_side=='right'
   app['cfg']['keys']={'OpenAI':'test-only-key'};app['save']()
   assert 'test-only-key' not in Path(temp,'settings.json').read_text(encoding='utf8')
   print('PASS: neon dashboard, 8 Settings tabs, validation/save, six page/back routes, three sizes, secure save')
  finally:
   app['advanced_manager'].close();app['personal_hub'].close();app['voice_hub'].close();app['con'].close();root.destroy()
 tk.Misc.mainloop=smoke
 try:
  import runpy
  runpy.run_path(str(base/'app.py'),run_name='__main__')
 finally:tk.Misc.mainloop=original


