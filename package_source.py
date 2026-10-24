"""Build the development source release without copying private runtime data."""
from pathlib import Path
import hashlib
import zipfile
from version import VERSION

root=Path(__file__).resolve().parent
out=root/'dist';out.mkdir(exist_ok=True)
package=out/f'SARU_AI_{VERSION}_source.zip'
files=[]
for item in root.iterdir():
 if item.is_file() and (item.suffix in ('.py','.md','.bat','.txt','.png','.jpg','.gif','.ico','.ps1') or item.name=='.gitignore') and item.name not in ('settings.json','memory.db'):
  files.append(item)
files.extend(p for p in (root/'MYRA_OFFICIAL_GUIDES').rglob('*') if p.is_file())
from advanced_workspace import bundle_manifest
if (root/'mark_suite/SOURCE_INVENTORY.json').exists():
 manifest=bundle_manifest(root);files.extend(root/'mark_suite'/entry['path'] for entry in manifest['files']);files.append(root/'mark_suite/SOURCE_INVENTORY.json')
with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as archive:
 for file in sorted(files):archive.write(file,f'SARU_AI_{VERSION}/'+file.relative_to(root).as_posix())
digest=hashlib.sha256(package.read_bytes()).hexdigest()
package.with_suffix('.zip.sha256').write_text(digest+'  '+package.name+'\n',encoding='ascii')
with zipfile.ZipFile(package) as archive:
 assert archive.testzip() is None
 for required in ('app.py','dashboard_ui.py','settings_store.py','installer.py','MASTER_SPEC.md'):
  assert f'SARU_AI_{VERSION}/'+required in archive.namelist()
print('Source archive verified:',package)
