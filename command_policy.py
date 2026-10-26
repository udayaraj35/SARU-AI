"""Direct explicit owner commands; inner source/file/account reviews stay independent."""
DIRECT={'self_improve','app','notepad','browser','site','named_app','select_app','desktop_task','pc_control','settings','document_editor','repo_center','office','office_status','media_player','video_studio','updates','diagnostics','downloads','search','youtube_search','volume','brightness','help','status','calculate','notes','recall','ui_control'}
CONTROL={'lifecycle','edit','edit_files','edit_request','settings','view','theme','photo_size','text_size','portrait','window','browser','browser_tab','voice','controls','control_help','page','orb_size','orb_text_size','orb_opacity','orb_visible','reduced_motion','companion_style','speak','voice_rate','auto_listen','remember_conversations','invalid_setting','screen','screen_window','screen_task','screen_watch'}

def direct_owner_action(action,arg=None):
 if action=='saru_control' and isinstance(arg,(tuple,list)) and arg[0] in ('navigation','settings_tab'):return True
 if action=='saru_control' and isinstance(arg,(tuple,list)) and arg[0]=='chat':return True
 if action=='backend':return True # Each backend operation applies its own exact review.
 if action in ('media_search','media_control','media_play','media_save'):return True
 if action in ('wacrm_panel','wacrm_read'):return True
 if action=='desktop_input':return True
 return action in DIRECT or (action=='saru_control' and isinstance(arg,(tuple,list)) and arg[0] in CONTROL)
