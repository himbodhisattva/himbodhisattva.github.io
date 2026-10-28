#!/usr/bin/env python3
"""Apply the media mapping to data.js. No network access; no publishing."""
from pathlib import Path
from urllib.parse import urlparse, unquote
import argparse,json,re,sys
ROOT=Path(__file__).resolve().parent.parent

def load_data():
    text=(ROOT/'data.js').read_text()
    return json.loads(re.sub(r'^window\.ANS_DATA\s*=\s*','',text).rstrip().removesuffix(';'))

def check_path(value, label):
    if value is None:return
    if not isinstance(value,str) or not value:raise ValueError(f'{label}: use a path or null')
    parsed=urlparse(value)
    if parsed.scheme:
        if parsed.scheme!='https':raise ValueError(f'{label}: only relative paths or https URLs are allowed')
        return
    if value.startswith('/'):
        print(f'NOTE {label}: root-relative URL must exist on your host: {value}')
        return
    path=(ROOT/unquote(parsed.path)).resolve()
    if not path.is_relative_to(ROOT):raise ValueError(f'{label}: path escapes the site directory')
    if not path.is_file():raise ValueError(f'{label}: file not found: {value}')

def main():
    p=argparse.ArgumentParser();p.add_argument('manifest',nargs='?',type=Path,default=ROOT/'media-manifest.json');a=p.parse_args()
    data=load_data();manifest=json.loads(a.manifest.read_text());known_t={x['id'] for x in data['tracks']};known_a={x['id'] for x in data['albums']}
    unknown=set(manifest.get('tracks',{}))-known_t | (set(manifest.get('albums',{}))-known_a)
    if unknown:raise ValueError('Unknown catalog IDs: '+', '.join(sorted(unknown)))
    for item in data['albums']:
        m=manifest.get('albums',{}).get(item['id'],{})
        if 'art' in m:check_path(m['art'],item['id']+' artwork');item['art']=m['art']
    for item in data['tracks']:
        m=manifest.get('tracks',{}).get(item['id'],{})
        for key in ('audio','art'):
            if key in m:check_path(m[key],item['id']+' '+key);item[key]=m[key]
    (ROOT/'data.js').write_text('window.ANS_DATA = '+json.dumps(data,ensure_ascii=False)+';\n')
    print(f"Applied mapping: {sum(bool(t['audio']) for t in data['tracks'])}/{len(data['tracks'])} recordings configured. Nothing published.")
if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,json.JSONDecodeError,OSError) as e:print('ERROR:',e,file=sys.stderr);sys.exit(1)
