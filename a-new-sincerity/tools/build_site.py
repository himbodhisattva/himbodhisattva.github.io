#!/usr/bin/env python3
"""Build a static folder for /a-new-sincerity/. Does not upload or deploy."""
from pathlib import Path
import argparse,shutil,json,re
ROOT=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser();p.add_argument('--publish',action='store_true',help='replace noindex with canonical links in the built copy only; does NOT deploy');args=p.parse_args()
out=ROOT/'dist'/'a-new-sincerity'
if out.exists():shutil.rmtree(out)
out.mkdir(parents=True,exist_ok=True)
for name in ['index.html','style.css','experience.css','app.js','player-model.js','data.js','lyrics-sync.js','favicon.ico']:shutil.copy2(ROOT/name,out/name)
for name in ['assets','audio','records']:
 if (ROOT/name).exists():shutil.copytree(ROOT/name,out/name,dirs_exist_ok=True)
if args.publish:
 for relative,canonical in [('index.html','https://himbodhisattva.com/a-new-sincerity/'),('records/index.html','https://himbodhisattva.com/a-new-sincerity/records/')]:
  path=out/relative
  html=path.read_text().replace('<meta name="robots" content="noindex,nofollow">',f'<link rel="canonical" href="{canonical}">')
  path.write_text(html)
 print('Publication-mode folder prepared. Review audio, credits, privacy and final covers before uploading.')
else:print('Staging folder prepared with noindex retained.')
print(out)
print('No files were uploaded or published.')
