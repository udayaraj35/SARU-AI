"""Explicit first-run backend setup; downloads public model/browser, never user data."""
import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import sys


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--memory',action='store_true');parser.add_argument('--browser',action='store_true')
    parser.add_argument('--receipt',action='store_true')
    args=parser.parse_args()
    data=Path(os.getenv('SARU_DATA_DIR') or str(Path(os.getenv('APPDATA',str(Path.home())))/'SARU_AI'))
    if args.memory:
        from fastembed import TextEmbedding
        from memory_manager import MODEL
        model=TextEmbedding(MODEL,cache_dir=str(data/'embedding_models'),threads=2)
        vector=next(model.embed(['SARU setup check']))
        print('Local semantic model ready: '+str(len(vector))+' dimensions')
    if args.browser:
        env=dict(os.environ);env['PLAYWRIGHT_BROWSERS_PATH']=str(data/'advanced/browsers')
        subprocess.run([sys.executable,'-m','playwright','install','chromium'],env=env,check=True)
        print('Private Chromium browser ready')
    if args.receipt:
        from install_support import source_files
        from updater import atomic_json
        from version import VERSION
        root=Path(__file__).resolve().parent
        files={path.as_posix():hashlib.sha256((root/path).read_bytes()).hexdigest() for path in source_files(root)}
        atomic_json(data/'signed_updates/installed.json',{'version':VERSION,'files':files})
        print('Installed-source receipt initialized')
    if not args.memory and not args.browser and not args.receipt:parser.print_help()


if __name__=='__main__':main()
