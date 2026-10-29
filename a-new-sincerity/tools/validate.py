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
track_by_id={t['id']:t for t in data['tracks']}
manifest=json.loads((ROOT/'media-manifest.json').read_text())
assert album_by_id['revisionist']['artist'].lower()=='a new sincerity'
assert album_by_id['revisionist']['group']=='ans', 'Revisionist History belongs to A New Sincerity'
assert album_by_id['victory-lap']['art']=='assets/user/victory-lap-1254.webp', 'Victory Lap must use the high-resolution cover'
assert album_by_id['friday-girls']['art']=='assets/user/friday-girls-1254.webp', 'Friday Girls must use the high-resolution cover'
assert track_by_id['friday-girls-05']['art']=='assets/user/friday-girls-again-and-again.webp', 'Again and Again must use its track artwork'
assert all(manifest['albums'][a['id']]['art']==a['art'] for a in data['albums']), 'album artwork paths disagree with the media manifest'
assert all(manifest['tracks'][t['id']]['art']==t['art'] and manifest['tracks'][t['id']]['audio']==t['audio'] for t in data['tracks']), 'track media paths disagree with the media manifest'
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
 external_runtime_urls=re.findall(r'<(?:script|link)[^>]+(?:src|href)="(https?://[^"]+)"',html)
 allowed_runtime_urls={'https://platform.twitter.com/widgets.js'} if document == ROOT/'index.html' else set()
 assert set(external_runtime_urls)<=allowed_runtime_urls, f'{document.name}: unexpected runtime dependency'
 wordmark=re.search(r'<a class="site-wordmark".*?</a>',html,re.S).group()
 assert 'himbodhisattva' not in wordmark.lower(), f'{document.name}: project should not carry the parent-site brand'
 for path in re.findall(r'(?:src|href)="(assets/[^\"]+)"',html):assert (ROOT/path).is_file(),path
main=documents[0].read_text()
records=documents[1].read_text()
public_copy=(main+records).lower()
assert '<details' not in main and '<summary' not in main, 'story should avoid stacked accordions'
assert 'Minima' not in main and 'minima' not in main, 'Minima should remain in the catalog, not the essay focus'
assert 'Like They Do In The Movies' in main
assert 'somehow both a victory lap and a cry for help' in main.lower()
assert 'emulated stereogum' in main.lower()
assert 'data-play="victory-lap-01"' in main
assert 'Hyperpop-punk, sincerity and self-absorption cranked up.' in main
assert 'data-album-embed="unfortunately"' in main
assert 'data-album-embed="revisionist"' in main
assert 'data-album-embed="friday-girls"' in main
assert 'emulated-review' in main and 'not published by' in main.lower()
assert 'AI reconstruction from a recording where the original performance is barely audible' in main
assert 'the creation changed its creator' in main.lower()
assert 'the map modifies the territory' in main.lower()
assert 'twitter-tweet' in main and 'platform.twitter.com/widgets.js' in main
assert 'id="liner-notes"' not in main and 'review-centerpiece' not in main and 'current-status' not in main
assert main.count('class="records-door"') == 1
assert 'get in loser, we\'re subverting postmodernism from the inside' in main
assert 'attached' not in (main+records+(ROOT/'app.js').read_text()).lower(), 'stale attachment copy remains'
assert 'id="records"' not in main, 'the full catalog belongs on its own page'
assert 'id="records"' in records and 'id="album-stage"' in records
assert 'id="lyric-stage"' in main and 'id="lyric-stage"' in records
assert main.index('id="unfortunately"') < main.index('id="counterfactual"'), '(unfortunately) must precede Revisionist History'
for recommendation in ('our favorite', 'start with', 'places to start', 'save this one for later', 'funniest song'):
 assert recommendation not in public_copy, f'recommendation copy remains: {recommendation}'
records_hero=re.search(r'<header class="records-hero">(.*?)</header>',records,re.S).group(1)
assert re.sub(r'<[^>]+>','',records_hero).strip()=='the records.', 'records page hero should say only “the records.”'
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
