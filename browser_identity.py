"""Report the actual bundled Chromium version without Qt's extra compatibility token."""
import re

def compatible_user_agent(default,chromium_version):
 if not re.fullmatch(r'\d+\.\d+\.\d+\.\d+',chromium_version):raise ValueError('Invalid actual Chromium version')
 result=re.sub(r'\s+QtWebEngine/[\d.]+','',default)
 result=re.sub(r'Chrome/[\d.]+','Chrome/'+chromium_version,result)
 return result
