#!/usr/bin/env python3
"""Build an in-place HTML preview with inlined images, CSS and JavaScript.

The preview stays in the app root so its relative audio paths keep working. It
is not a portable single file because the recordings remain in audio/.
"""
from pathlib import Path
import base64, json, re
ROOT = Path(__file__).resolve().parent.parent

def build(destination: Path) -> None:
    assets = {}
    for p in (ROOT/'assets').rglob('*'):
        if p.is_file() and p.suffix.lower() in {'.webp','.jpg','.jpeg','.png','.svg'}:
            media = {'.webp':'image/webp','.jpg':'image/jpeg','.jpeg':'image/jpeg','.png':'image/png','.svg':'image/svg+xml'}[p.suffix.lower()]
            assets[p.relative_to(ROOT).as_posix()] = 'data:'+media+';base64,'+base64.b64encode(p.read_bytes()).decode()
    html = (ROOT/'index.html').read_text()
    css=(ROOT/'style.css').read_text()+'\n'+(ROOT/'experience.css').read_text()
    html = html.replace('<link rel="stylesheet" href="style.css">','<style>'+css+'</style>').replace('<link rel="stylesheet" href="experience.css">','')
    for source in ['data.js','lyrics-sync.js','player-model.js','app.js']:
        html=html.replace(f'<script defer src="{source}"></script>','')
    for path, value in assets.items():
        html=html.replace('src="'+path+'"','src="'+value+'"').replace('href="'+path+'"','href="'+value+'"')
    js='window.ANS_ASSETS = '+json.dumps(assets)+';\n'+'\n'.join((ROOT/source).read_text() for source in ['data.js','lyrics-sync.js','player-model.js','app.js'])
    # Prevent any user-supplied lyric text from accidentally ending the inline script.
    js=re.sub(r'</script',r'<\\/script',js,flags=re.IGNORECASE)
    html=html.replace('</body>','<script>'+js+'</script></body>')
    destination.write_text(html)
    print(f'Built {destination.name}: {destination.stat().st_size:,} bytes')
if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('output',nargs='?',type=Path,default=ROOT/'local-preview.html')
    build(parser.parse_args().output)
