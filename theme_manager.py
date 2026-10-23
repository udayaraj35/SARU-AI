"""Persistent color themes for native widgets; reference photos remain original."""
import tkinter as tk
from tkinter import ttk

THEMES={
 'Neon Rose':{'bg':'#060810','panel':'#1b1f2c','field':'#0b0e18','line':'#414655','accent':'#13c8ec','primary':'#ff285c','text':'#f3f4fc','muted':'#aeb6cf'},
 'Cyber Violet':{'bg':'#100c24','panel':'#201735','field':'#130e29','line':'#584080','accent':'#b18cff','primary':'#ed65e4','text':'#f2eaff','muted':'#bdb0d4'},
 'Ocean Cyan':{'bg':'#03191e','panel':'#082830','field':'#041d23','line':'#21555d','accent':'#48e1db','primary':'#23b7df','text':'#e5fbff','muted':'#9bc5ce'},
 'Emerald Night':{'bg':'#071b16','panel':'#0c2b22','field':'#081e18','line':'#285b48','accent':'#51e6ac','primary':'#37be8d','text':'#e9fff5','muted':'#a1c7b5'},
}
SOURCE={
 'bg':['#061226','#07080e','#071326','#07142a','#060d20','#090914','#061025','#07080e'],
 'panel':['#0b1930','#101119','#09152a','#101526','#14111b','#150d24','#101526'],
 'field':['#081225','#040911','#11213a'],
 'line':['#284c70','#25445f','#244460','#3a2435'],
 'accent':['#18cde2','#18cde2','#16cafa','#48d8ff','#57d9ff'],
 'primary':['#ff2856','#fd2f8c','#ff348c'],
 'text':['#edf4ff'], 'muted':['#9cb0cf','#a4c4dd'],
}

def palette(name):return THEMES.get(name,THEMES['Neon Rose'])

def apply_theme(widget,name,configure_styles=True):
 colors=palette(name);mapping={value:colors[role] for role,values in SOURCE.items() for value in values}
 # Also recognize colors from another theme so a switch can be applied in place.
 for theme in THEMES.values():
  for role,value in theme.items():mapping[value]=colors[role]
 def apply(item):
  try:
   for option in ('background','foreground','activebackground','activeforeground','highlightbackground','highlightcolor','insertbackground','selectcolor','troughcolor'):
    if option in item.keys():
     current=str(item.cget(option)).lower()
     if current in mapping and mapping[current]!=current:item.configure(**{option:mapping[current]})
   if isinstance(item,tk.Canvas):
    for element in item.find_all():
     for option in ('fill','outline'):
      try:
       value=item.itemcget(element,option).lower()
       if value in mapping and mapping[value]!=value:item.itemconfigure(element,**{option:mapping[value]})
      except tk.TclError:pass
   if hasattr(item,'paint') and getattr(item,'theme_palette',None)!=colors:
    item.theme_palette=dict(colors);item.last_size=None
    item.paint(max(20,item.winfo_width()),max(20,item.winfo_height()))
  except tk.TclError:pass
  for child in item.winfo_children():apply(child)
 apply(widget)
 if not configure_styles:return
 root=widget._root()
 style=ttk.Style(widget)
 if style.theme_use()!='clam':
  style.theme_use('clam');root._saru_ttk_theme=None
 if getattr(root,'_saru_ttk_theme',None)==name:return
 root._saru_ttk_theme=name
 style.configure('TNotebook',background=colors['bg'])
 style.configure('TNotebook.Tab',background=colors['panel'],foreground=colors['text'])
 style.map('TNotebook.Tab',background=[('selected',colors['line']),('active',colors['panel'])],foreground=[('selected',colors['text'])])
 style.configure('TCombobox',fieldbackground=colors['field'],background=colors['panel'],foreground=colors['text'],arrowcolor=colors['accent'])

 # Explicit state colors prevent white-on-white readonly fields on Windows.
 for widget_style in ('TCombobox','TEntry','TSpinbox'):
  style.configure(widget_style,fieldbackground=colors['field'],foreground=colors['text'],insertcolor=colors['accent'],selectbackground=colors['line'],selectforeground=colors['text'])
  style.map(widget_style,fieldbackground=[('disabled',colors['panel']),('readonly',colors['field'])],foreground=[('disabled',colors['muted']),('readonly',colors['text'])],selectforeground=[('!disabled',colors['text'])],selectbackground=[('!disabled',colors['line'])])
 root.option_add('*TCombobox*Listbox.background',colors['field'])
 root.option_add('*TCombobox*Listbox.foreground',colors['text'])
 root.option_add('*TCombobox*Listbox.selectBackground',colors['line'])
 root.option_add('*TCombobox*Listbox.selectForeground',colors['text'])
