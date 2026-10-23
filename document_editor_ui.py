"""Local exact-replacement document editor with immutable owner review."""
import threading,tkinter as tk
from tkinter import filedialog
from queue import Queue,Empty
from pathlib import Path
from PIL import Image,ImageTk
from document_editing import fingerprint,replace_text

class DocumentEditor(tk.Toplevel):
 def __init__(self,root,consent,report,config=None):
  super().__init__(root);self.title('SARU · PDF / Word text editor');self.geometry('980x760');self.consent=consent;self.report=report;self.closed=False;self.busy=False;self.events=Queue();self.job=None;self.photos=[]
  self.config_data=config or {}
  tk.Label(self,text='PDF / Word · Preserve font and size · Save a new copy',font=('Segoe UI',15,'bold')).pack(pady=10)
  tk.Label(self,text='Exact text replacement only. PDF: one complete text span, no OCR/scans or font substitution. DOCX: one formatted text node; review Word pagination.',wraplength=920).pack(fill='x',padx=12)
  self.source=tk.StringVar();self.target=tk.StringVar();self.old=tk.StringVar();self.new=tk.StringVar()
  for name,var in [('Original file',self.source),('Save new copy as',self.target),('Exact old text',self.old),('Replacement text',self.new)]:
   tk.Label(self,text=name).pack(anchor='w',padx=14);tk.Entry(self,textvariable=var).pack(fill='x',padx=14,pady=4)
  tk.Button(self,text='Choose original PDF / DOCX',command=self.choose).pack(pady=3)
  tk.Button(self,text='Review and save edited copy',command=self.review).pack(pady=6)
  self.status=tk.Label(self,text='No document changed.',wraplength=920);self.status.pack(fill='x',padx=12)
  self.preview=tk.Canvas(self,bg='#182235',height=330);self.preview.pack(fill='both',expand=True,padx=12,pady=10)
  self.bind('<Destroy>',self.cleanup,add='+');self.pump()
 def choose(self):
  path=filedialog.askopenfilename(parent=self,filetypes=[('Documents','*.pdf *.docx')])
  if path:
   self.source.set(path);p=Path(path);self.target.set(str(p.with_name(p.stem+'-edited'+p.suffix)))
 def review(self):
  if self.busy:return
  from work_storage import ask_work_save
  source=Path(self.source.get())
  if not source.is_file() or source.suffix.lower() not in ('.pdf','.docx'):self.status.configure(text='Choose an existing PDF or DOCX first.');return
  chosen=ask_work_save(self.config_data,parent=self,defaultextension=source.suffix,initialfile=source.stem+'-edited'+source.suffix,filetypes=[('Document','*'+source.suffix)])
  if not chosen:return
  self.target.set(chosen)
  values=tuple(var.get() for var in (self.source,self.target,self.old,self.new))
  try:
   from document_editing import validate
   validate(*values);digest=fingerprint(values[0])
  except Exception as exc:self.status.configure(text=str(exc));return
  def approved():
   if self.closed or self.busy:raise ValueError('Document editor is closed/busy.')
   if values!=tuple(var.get() for var in (self.source,self.target,self.old,self.new)):raise ValueError('Document request changed. Review again.')
   self.busy=True;self.status.configure(text='Checking formatting and saving a new copy…')
   def work():
    try:result=replace_text(*values,expected=digest);self.events.put((result,values[0],values[1]))
    except Exception as exc:self.events.put(('Document edit rejected: '+str(exc),None,None))
   threading.Thread(target=work,daemon=True).start()
  self.consent('Save new document copy? '+values[0]+' → '+values[1]+'\nReplace '+repr(values[2])+' with '+repr(values[3])+'. Font/size substitution is disabled. Review output before use.',approved,seconds=90)
 def show_preview(self,source,target):
  self.preview.delete('all');self.photos=[]
  if not source.lower().endswith('.pdf'):
   self.preview.create_text(450,100,text='DOCX font/run properties preserved. Open the new copy in Word to verify wrapping, pagination and layout.',fill='white',width=800);return
  import pymupdf as fitz
  for index,path in enumerate((source,target)):
   with fitz.open(path) as doc:
    page=next((p for p in doc if p.search_for(self.new.get() if index else self.old.get())),doc[0]);pix=page.get_pixmap(matrix=fitz.Matrix(.65,.65),alpha=False)
    image=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);image.thumbnail((440,300));photo=ImageTk.PhotoImage(image);self.photos.append(photo)
    self.preview.create_text(230+index*460,14,text='Original' if index==0 else 'Edited copy',fill='white');self.preview.create_image(230+index*460,34,image=photo,anchor='n')
 def pump(self):
  if self.closed:return
  try:
   result,source,target=self.events.get_nowait();self.busy=False;self.status.configure(text=result);self.report(result+(' '+target if target else ''))
   if target:
    try:self.show_preview(source,target)
    except Exception as exc:self.status.configure(text=result+' Preview unavailable: '+str(exc))
  except Empty:pass
  self.job=self.after(150,self.pump)
 def cleanup(self,event):
  if event.widget is self:
   self.closed=True
   if self.job:self.after_cancel(self.job)
