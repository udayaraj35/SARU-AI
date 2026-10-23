"""Real local deliverables; atomic writes and no executable spreadsheet cells."""
from pathlib import Path
import os
import tempfile
import textwrap
from PIL import Image,ImageDraw,ImageFont

def font(size):
 folder=Path(os.environ.get('WINDIR',r'C:\Windows'))/'Fonts'
 for name in ('Nirmala.ttf','nirmala.ttf','arial.ttf'):
  try:return ImageFont.truetype(str(folder/name),size)
  except OSError:pass
 raise ValueError('A Windows Unicode font is required to export PDF/video text.')

def lines(text,width=85):
 result=[]
 for paragraph in text.splitlines():result.extend(textwrap.wrap(paragraph,width=width,replace_whitespace=False) or [''])
 return result

def export_result(result,format,path):
 path=Path(path)
 if format not in ('txt','docx','xlsx','pdf','mp4') or path.suffix.lower()!='.'+format:raise ValueError('Choose the matching file extension.')
 if not path.parent.is_dir():raise ValueError('Choose an existing destination folder.')
 fd,temporary=tempfile.mkstemp(prefix='.saru-office-',suffix='.'+format,dir=path.parent);os.close(fd);temp=Path(temporary)
 complete=result['body']
 for item in result.get('tables',[]):complete+='\n\n'+str(item.get('name','Table'))+'\n'+'\n'.join(' | '.join(map(str,row)) for row in item['rows'])
 try:
  if format=='txt':temp.write_text(result['title']+'\n\n'+complete,encoding='utf8')
  elif format=='docx':
   from docx import Document
   from docx.shared import Pt
   from docx.oxml import OxmlElement
   from docx.oxml.ns import qn
   doc=Document();style=doc.styles['Normal'];style.font.name='Nirmala UI';style.font.size=Pt(11)
   fonts=style.element.get_or_add_rPr().get_or_add_rFonts();fonts.set(qn('w:cs'),'Nirmala UI')
   doc.add_heading(result['title'],0)
   for paragraph in result['body'].splitlines():doc.add_paragraph(paragraph)
   for item in result.get('tables',[]):
    rows=item.get('rows',[])
    if not rows:continue
    doc.add_heading(str(item.get('name','Table')),2);table=doc.add_table(rows=0,cols=max(len(row) for row in rows) or 1);table.style='Table Grid'
    for row in rows:
     cells=table.add_row().cells
     for index,value in enumerate(row):cells[index].text=str(value)
   doc.save(temp)
  elif format=='xlsx':
   from openpyxl import Workbook
   from openpyxl.styles import Font,PatternFill,Alignment
   workbook=Workbook();sheet=workbook.active;sheet.title='SARU Summary';sheet.append([result['title']])
   for paragraph in result['body'].splitlines():sheet.append([paragraph[:32767]])
   for index,item in enumerate(result.get('tables',[])):
    table=workbook.create_sheet('Table '+str(index+1))
    for row in item.get('rows',[]):table.append([str(value)[:32767] for value in row])
   for sheet in workbook:
    sheet.freeze_panes='A2'
    for row in sheet:
     for cell in row:
      if isinstance(cell.value,str):cell.data_type='s'
      cell.alignment=Alignment(wrap_text=True,vertical='top');cell.font=Font(name='Nirmala UI',size=11)
    for cell in sheet[1]:cell.font=Font(name='Nirmala UI',bold=True,color='FFFFFF');cell.fill=PatternFill('solid',fgColor='16304F')
    sheet.column_dimensions['A'].width=90 if sheet.title=='SARU Summary' else 30
   workbook.save(temp)
  elif format=='pdf':
   # Raster text pages preserve Windows complex-script shaping without relying
   # on the recipient having Nepali fonts. These PDFs are not searchable text.
   content=lines(result['title']+'\n\n'+result['body'])
   for table in result.get('tables',[]):
    content+=lines('\n'+str(table.get('name','Table'))+'\n'+'\n'.join(' | '.join(map(str,row)) for row in table['rows']))
   if len(content)>1000:raise ValueError('PDF exceeds the 20-page export limit. Save the full draft as DOCX or TXT.')
   pages=[];face=font(24)
   for offset in range(0,len(content),50):
    page=Image.new('RGB',(1240,1754),'white');draw=ImageDraw.Draw(page)
    for index,line in enumerate(content[offset:offset+50]):draw.text((70,65+index*32),line,font=face,fill='#101526')
    draw.text((70,1690),'SARU Office · '+str(offset//50+1),font=font(18),fill='#536477');pages.append(page)
   pages[0].save(temp,'PDF',resolution=150,save_all=True,append_images=pages[1:])
  else:
   from video_creator import create_video
   content=lines(complete,width=48)
   if len(content)>96:raise ValueError('Short video supports up to 96 wrapped lines; save the full document separately.')
   with tempfile.TemporaryDirectory(prefix='.office-slides-',dir=path.parent) as folder:
    images=[]
    for offset in range(0,max(1,len(content)),8):
     image=Image.new('RGB',(1280,720),'#061226');draw=ImageDraw.Draw(image)
     draw.text((55,35),result['title'][:50],font=font(36),fill='#18cde2')
     for index,line in enumerate(content[offset:offset+8]):draw.text((55,130+index*56),line,font=font(30),fill='#edf4ff')
     target=Path(folder)/(str(offset)+'.png');image.save(target);images.append(target)
    create_video(images,[],temp,seconds=4)
  os.replace(temp,path)
 finally:temp.unlink(missing_ok=True)
 return path
