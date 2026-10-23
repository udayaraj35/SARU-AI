"""Reviewed exact text replacements saved as new PDF/DOCX copies."""
import hashlib,io,os,tempfile,zipfile
from pathlib import Path
from lxml import etree


def fingerprint(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate(source,target,old,new):
 source=Path(source).resolve();target=Path(target).resolve()
 if source.stat().st_size>100*1024*1024:raise ValueError('Choose a document under 100 MB.')
 if source==target:raise ValueError('Save to a new copy; original overwrite is disabled.')
 if target.exists():raise ValueError('Output already exists; choose a new file name.')
 if source.suffix.lower() not in ('.pdf','.docx') or source.suffix.lower()!=target.suffix.lower():raise ValueError('Choose PDF or DOCX with matching output type.')
 if not old or not new or old==new or len(old)>4000 or len(new)>4000 or any(ord(c)<32 for c in old+new):raise ValueError('Use distinct single-line text up to 4000 characters.')
 return source,target


def edit_docx(source,target,old,new):
 # Preserve all package entries, run properties, styles and media. Never rebuild paragraphs.
 ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
 with zipfile.ZipFile(source) as archive:
  if sum(i.file_size for i in archive.infolist())>200*1024*1024:raise ValueError('Expanded DOCX package exceeds 200 MB.')
  if any(i.filename.startswith('_xmlsignatures/') for i in archive.infolist()):raise ValueError('Signed DOCX requires a separate signing workflow.')
  hits=[];parts={}
  for name in archive.namelist():
   if name.startswith('word/') and name.endswith('.xml'):
    root=etree.fromstring(archive.read(name),parser=etree.XMLParser(resolve_entities=False,no_network=True));parts[name]=root
    for node in root.xpath('//w:t',namespaces=ns):
     if old in (node.text or ''):hits.extend((name,node) for _ in range(node.text.count(old)))
  if len(hits)!=1:raise ValueError('Find exactly one occurrence within a single formatted text run; split-run/ambiguous matches need manual review.')
  name,node=hits[0];node.text=node.text.replace(old,new,1)
  if node.text!=node.text.strip():node.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
  with zipfile.ZipFile(target,'w') as output:
   for item in archive.infolist():output.writestr(item,etree.tostring(parts[name],xml_declaration=True,encoding='UTF-8',standalone=True) if item.filename==name else archive.read(item.filename))
 return 'DOCX copy saved. Run font/size/styles and untouched package parts preserved. Open in Word to verify wrapping and pagination.'


def edit_pdf(source,target,old,new):
 import pymupdf as fitz
 from PIL import Image,ImageChops,ImageDraw
 doc=fitz.open(source)
 try:
  if doc.needs_pass or doc.is_encrypted:raise ValueError('Encrypted PDF is not supported by this editor.')
  if doc.get_sigflags()>0:raise ValueError('Signed/signature-enabled PDF requires a separate workflow.')
  hits=[]
  for page in doc:
   for block in page.get_text('dict')['blocks']:
    for line in block.get('lines',[]):
     for span in line['spans']:
      if span['text']==old:hits.append((page.number,line,span))
  if len(hits)!=1:raise ValueError('PDF edit requires exactly one complete text span. Scans, split spans and ambiguous matches are not changed.')
  number,line,span=hits[0];page=doc[number];rect=fitz.Rect(span['bbox'])
  if tuple(line.get('dir',(1,0)))!=(1.,0.) or line.get('wmode',0):raise ValueError('Rotated/vertical PDF text is not supported.')
  for block in page.get_text('dict')['blocks']:
   for other_line in block.get('lines',[]):
    for other in other_line['spans']:
     if other is span:continue
     if other['text']==old and tuple(other['bbox'])==tuple(span['bbox']):continue
     if not (rect & fitz.Rect(other['bbox'])).is_empty:raise ValueError('Text overlaps another span; refusing to change nearby text.')
  bases={'Helvetica':'helv','Helvetica-Bold':'hebo','Helvetica-Oblique':'heit','Helvetica-BoldOblique':'hebi','Times-Roman':'tiro','Times-Bold':'tibo','Times-Italic':'tiit','Times-BoldItalic':'tibi','Courier':'cour','Courier-Bold':'cobo','Courier-Oblique':'coit','Courier-BoldOblique':'cobi'}
  buffer=None;fontname=bases.get(span['font']);font=None
  if fontname:font=fitz.Font(fontname)
  else:
   for item in page.get_fonts(full=True):
    if item[3].split('+')[-1]==span['font'].split('+')[-1]:
     extracted=doc.extract_font(item[0]);buffer=extracted[3]
     if buffer:font=fitz.Font(fontbuffer=buffer);fontname='SaruPreserved';break
  if font is None:raise ValueError('Original font cannot be reused; no font substitution is allowed.')
  if any(not font.has_glyph(ord(char)) for char in new):raise ValueError('Original font lacks replacement glyphs; no font substitution allowed.')
  if font.text_length(new,fontsize=span['size'])>rect.width+.25:raise ValueError('Replacement is wider than the original area. Shorten text; font size will not be reduced.')
  before=page.get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False)
  page.add_redact_annot(rect,fill=None);page.apply_redactions(images=0,graphics=0,text=0)
  if buffer:page.insert_font(fontname=fontname,fontbuffer=buffer)
  color=span.get('color',0);rgb=tuple(((color>>shift)&255)/255 for shift in (16,8,0))
  page.insert_text(span['origin'],new,fontname=fontname,fontsize=span['size'],color=rgb)
  after=page.get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False)
  a=Image.frombytes('RGB',(before.width,before.height),before.samples);b=Image.frombytes('RGB',(after.width,after.height),after.samples)
  delta=ImageChops.difference(a,b);mask=Image.new('L',a.size,255);draw=ImageDraw.Draw(mask);draw.rectangle((max(0,int(rect.x0*1.5)-3),max(0,int(rect.y0*1.5)-3),int(rect.x1*1.5)+3,int(rect.y1*1.5)+3),fill=0)
  if ImageChops.multiply(delta,Image.merge('RGB',(mask,mask,mask))).getbbox():raise ValueError('Rendered content changed outside the target area; copy rejected.')
  candidates=[s for block in page.get_text('dict')['blocks'] for ln in block.get('lines',[]) for s in ln['spans'] if s['text']==new]
  if not candidates or abs(candidates[-1]['size']-span['size'])>.01:raise ValueError('Replacement text/font size verification failed.')
  doc.save(target,garbage=4,deflate=True)
 finally:doc.close()
 return 'PDF copy saved. Original font/size/color reused; pixels outside the target text area verified unchanged. Review the preview before use.'


def replace_text(source,target,old,new,expected=None):
 source,target=validate(source,target,old,new)
 if expected and fingerprint(source)!=expected:raise ValueError('Source changed since review. Request a fresh review.')
 target.parent.mkdir(parents=True,exist_ok=True)
 fd,temp=tempfile.mkstemp(suffix=target.suffix,dir=target.parent);os.close(fd);temp=Path(temp)
 try:
  result=(edit_pdf if source.suffix.lower()=='.pdf' else edit_docx)(source,temp,old,new)
  if expected and fingerprint(source)!=expected:raise ValueError('Source changed during edit. Copy rejected.')
  # Exclusive creation prevents overwriting a file that appeared after review.
  created=False
  try:
   with target.open('xb') as output:
    created=True;output.write(temp.read_bytes())
  except Exception:
   if created:target.unlink(missing_ok=True)
   raise
  return result
 finally:temp.unlink(missing_ok=True)
