#!/usr/bin/env python3
"""Dependency-free catalog, route and source checks. Run browser tests separately."""
from pathlib import Path
import re,json,sys
ROOT=Path(__file__).resolve().parent.parent
text=(ROOT/'data.js').read_text();data=json.loads(re.sub(r'^window\.ANS_DATA\s*=\s*','',text).rstrip().removesuffix(';'))
ids=[x['id'] for x in data['tracks']]
assert len(ids)==len(set(ids)), 'duplicate track IDs'
assert len(data['tracks'])==48 and len(data['albums'])==6
assert not any('entertainment' in a['artist'].lower() for a in data['albums'])
assert all(t['lyrics'].strip() and t['source'] for t in data['tracks'])
assert all(t in ids for a in data['albums'] for t in a['tracks'])
assert all(t in ids for t in data['queue'])
album_by_id={a['id']:a for a in data['albums']}
assert album_by_id['revisionist']['artist'].lower()=='a new sincerity'
assert album_by_id['revisionist']['group']=='ans', 'Revisionist History belongs to A New Sincerity'
assert all(t['group']==album_by_id[t['album']]['group'] for t in data['tracks']), 'track and album groups disagree'
assert data['defaultTrack']=='victory-lap-01', 'Victory Lap should be the site-wide player default'
assert data['queue'][0]=='victory-lap-01', 'The story queue should begin at the site anchor'
for obj in data['albums']+data['tracks']:
 for key in ['art','audio']:
  value=obj.get(key)
  if not value:continue
  assert not value.startswith(('blob:','javascript:','data:')), f'non-publishable {key}: {value}'
  if not value.startswith(('https://','/')):assert (ROOT/value).is_file(), f'missing asset {value}'
documents=[ROOT/'index.html',ROOT/'records'/'index.html']
for document in documents:
 html=document.read_text()
 assert 'noindex,nofollow' in html, f'{document.name}: staging copy must remain noindex until explicitly published'
 assert 'autoplay' not in re.search(r'<audio.*?>',html).group(), f'{document.name}: audio must not autoplay on arrival'
 assert not re.search(r'<(?:script|link)[^>]+(?:src|href)="https?://',html), f'{document.name}: unexpected runtime dependency'
 assert 'himbodhisattva' not in html.lower(), f'{document.name}: project should not carry the parent-site brand'
 for path in re.findall(r'(?:src|href)="(assets/[^\"]+)"',html):assert (ROOT/path).is_file(),path
main=documents[0].read_text()
records=documents[1].read_text()
assert '<details' not in main and '<summary' not in main, 'story should use the shared liner-note deck, not stacked accordions'
assert 'Minima' not in main and 'minima' not in main, 'Minima should remain in the catalog, not the essay focus'
assert 'Like They Do In The Movies' in main
assert 'somehow both a victory lap and a cry for help' in main.lower()
assert 'emulated Stereogum review' in main
assert 'data-play="victory-lap-01"' in main
assert 'data-play="unfortunately-08" data-queue="album" data-album-context="unfortunately"' in main
assert 'attached' not in (main+records+(ROOT/'app.js').read_text()).lower(), 'stale attachment copy remains'
assert 'id="records"' not in main, 'the full catalog belongs on its own page'
assert 'id="records"' in records and 'id="album-stage"' in records
assert 'id="lyric-stage"' in main and 'id="lyric-stage"' in records
sync_text=(ROOT/'lyrics-sync.js').read_text()
sync=json.loads(re.sub(r'^window\.ANS_SYNC\s*=\s*','',sync_text).rstrip().removesuffix(';'))
vocal_ids={t['id'] for t in data['tracks'] if not t['instrumental']}
assert set(sync)==vocal_ids, 'every vocal track must retain a cue map'
for track_id,entry in sync.items():
 cues=entry['cues']
 assert cues and all(cue['text'].strip() for cue in cues),f'{track_id}: empty cue map'
 assert all(cue['start']<=cue['end'] for cue in cues),f'{track_id}: reversed cue'
 assert all(left['start']<=right['start'] for left,right in zip(cues,cues[1:])),f'{track_id}: unordered cues'
low_confidence=sorted(track_id for track_id,entry in sync.items() if entry.get('confidence',1)<.4)
if low_confidence:print('WARN: listen-check low-confidence lyric alignment:',', '.join(low_confidence))
assert (ROOT/'player-model.js').is_file()
print('PASS: catalog ownership, standalone records route, Victory Lap focus, player sources, cue maps and staging visibility.')
