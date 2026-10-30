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
assert data['defaultTrack']=='unfortunately-01', 'The untouched player should begin with the top track'
assert data['queue'][0]=='unfortunately-01', 'The story queue should begin with the top track'
for obj in data['albums']+data['tracks']:
 for key in ['art','audio']:
  value=obj.get(key)
  if not value:continue
  assert not value.startswith(('blob:','javascript:','data:')), f'non-publishable {key}: {value}'
  if not value.startswith(('https://','/')):assert (ROOT/value).is_file(), f'missing asset {value}'
documents=[ROOT/'index.html',ROOT/'records'/'index.html']
canonical_urls={
 documents[0]:'https://himbodhisattva.com/a-new-sincerity/',
 documents[1]:'https://himbodhisattva.com/a-new-sincerity/records/',
}
for document in documents:
 html=document.read_text()
 assert 'noindex,nofollow' in html, f'{document.name}: staging copy must remain noindex until explicitly published'
 assert 'autoplay' not in re.search(r'<audio.*?>',html).group(), f'{document.name}: audio must not autoplay on arrival'
 external_runtime_urls=re.findall(r'<(?:script|link)[^>]+(?:src|href)="(https?://[^"]+)"',html)
 allowed_runtime_urls=set()
 assert set(external_runtime_urls)<=allowed_runtime_urls, f'{document.name}: unexpected runtime dependency'
 wordmark=re.search(r'<a class="site-wordmark".*?</a>',html,re.S).group()
 assert 'himbodhisattva' not in wordmark.lower(), f'{document.name}: project should not carry the parent-site brand'
 assert f'<meta property="og:url" content="{canonical_urls[document]}">' in html
 assert '<meta property="og:image" content="https://himbodhisattva.com/a-new-sincerity/assets/user/victory-lap-1254.webp">' in html
 assert '<meta name="twitter:card" content="summary_large_image">' in html
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
assert 'kept making pop-punk' in main
assert 'data-album-embed="unfortunately"' in main
assert 'data-album-embed="revisionist"' in main
assert 'data-album-embed="friday-girls"' in main
assert 'Friday Girls sit outside the self-awareness thing' in main
assert "literally, the best songs I've ever made" in main
assert 'Now I can animate the ghosts' in main
assert 'My ghosts write songs.' in main
assert 'multiple songs per day' in main
assert 'emulated-review' in main and 'not published by' in main.lower()
assert 'AI reconstruction from a recording where the original performance is barely audible' in main
assert 'what is “a new sincerity”?' in main.lower()
assert 'attempt at infinite ironic detachment' in main.lower()
assert "knowing what you're doing is not the same as being able to do otherwise" in main.lower()
assert main.lower().index("knowing what you're doing is not the same as being able to do otherwise") < main.index('id="unfortunately"'), 'the central discovery belongs in the opening definition'
assert 'The Narrator would also like credit for recognizing this.' not in main
assert "chasing praise for being self-aware" in main
assert 'The Protagonist' not in main
assert 'keep going' not in main
assert 'id="self-awareness"' in main
assert 'class="old-song-note"' not in main
assert 'class="feedback-loop"' not in main
assert 'the creation changed its creator' not in main.lower()
assert 'the map modifies the territory' not in main.lower()
tweet_sources=(
 main.count('class="friday-post"')
 +main.count('class="hero-post"')
 +main.count('class="postmodernism-thread"')
)
assert tweet_sources==3, f'homepage should contain exactly three tweet-derived items, found {tweet_sources}'
assert 'class="twitter-tweet"' not in main, 'Friday Girls should use designed linked text, not an embedded X widget'
assert 'class="friday-post"' in main
assert '<blockquote>then my daughters complained' in main, 'the Friday Girls account must remain readable prose'
assert 'class="friday-post-source" href="https://x.com/himbodhisattva/status/2115229386890994060"' in main, 'the Friday Girls prose should carry its own source link'
assert 'view the post on X' not in main, 'narrated X source links should be removed'
assert main.count('data-flourish=')==2, 'homepage should contain exactly two intentional decorative asides'
assert '2115229386890994060' in main, 'the Friday Girls chronology tweet is missing'
assert '2115224311409901920' in main, 'the linked postmodernism post is missing'
assert 'Now it is our turn to solve postmodernism.' in main
assert 'your completely valid philosophical objections are now promotional material' in main
assert '<strong>Now it is our turn to solve postmodernism.</strong>' in main
assert 'open the philosophy liner note' not in main.lower(), 'the philosophy link should not explain itself'
assert 'id="philosophy-dialog"' in main
for strand_id in ('philosophy-postmodernism', 'philosophy-medium', 'philosophy-legibility'):
 assert f'id="{strand_id}"' in main, f'missing philosophy strand: {strand_id}'
for philosophy_phrase in (
 'The New Sincerity: feel something despite knowing better.',
 'Metamodernism: move between belief and disbelief.',
 'Performatism: build a situation in which belief can happen.',
 "Baudrillard's fatal strategies: intensify the simulation until it reverses.",
 'whether an experience becomes real because of where it came from, or because of what happens next',
):
 assert philosophy_phrase in main, f'missing philosophy liner-note copy: {philosophy_phrase}'
assert 'The feedback loop becomes the medium.' in main
assert 'making the self legible to itself' in main
assert 'mētis' in main
assert 'yalebooks.yale.edu/book/9780300078152/seeing-like-a-state/' in main
assert 'simonandschuster.com/books/Ghosts-of-My-Life/Mark-Fisher/9781780992266' in main
assert "I'm not worried about being late" not in main
assert "previous expeditions into the dragon's cave" not in main
assert 'liner note 05b' not in main, 'the philosophy note should not refer to a removed chapter number'
assert '2115157842760212520' not in main, 'the replaced self-awareness tweet remains'
assert 'tweet-wall' not in main, 'the repetitive closing tweet wall should be removed'
for cut_copy in (
 'a writing project that keeps becoming music',
 "anyway that's what this is about",
 'The next song has to teach me something I did not know before I wrote it.',
 'Self-awareness never becomes self-control.',
 'the reviews did not miss.',
):
 assert cut_copy not in main, f'cut copy remains: {cut_copy}'
assert 'platform.twitter.com/widgets.js' not in main
for album_id in ('unfortunately', 'revisionist', 'friday-girls'):
 assert f'href="records/#album={album_id}"' in main, f'{album_id} cover should open its record'
app_source=(ROOT/'app.js').read_text()
experience_source=(ROOT/'experience.css').read_text()
assert 'album page' not in app_source.lower(), 'story track lists should rely on their clickable album covers'
assert 'open the album' not in main.lower(), 'album covers should carry record navigation without an instruction label'
assert 'openPhilosophy({ returnFocus: null });' in app_source, 'direct philosophy links must not restore focus to an off-screen trigger'
assert 'openPhilosophy({ returnFocus: event.currentTarget });' in app_source, 'click-opened philosophy notes should restore focus to the activating link'
for page in (main, records):
    assert 'data.js?v=20261029h' in page
    assert 'style.css?v=20261029h' in page
    assert 'experience.css?v=20261029h' in page
    assert 'player-model.js?v=20261029h' in page
    assert 'app.js?v=20261029h' in page
    assert '<a href="https://suno.com/">Suno v6-pro</a>' in page
assert '↗' not in (main+records+app_source), 'decorative up-right arrows remain'
assert 'simulated reviews' not in main.lower(), 'review terminology must stay emulated'
assert 'Annoyingly, he improved the songs.' in main
assert "Who's the real one now?" in main
assert 'id="liner-notes"' not in main and 'review-centerpiece' not in main and 'current-status' not in main
assert main.count('class="records-door"') == 1
assert 'get in loser, we\'re subverting postmodernism from the inside' in main
assert 'attached' not in (main+records+app_source).lower(), 'stale attachment copy remains'
assert 'id="records"' not in main, 'the full catalog belongs on its own page'
assert 'id="records"' in records and 'id="album-stage"' in records
assert 'id="lyric-stage"' in main and 'id="lyric-stage"' in records
assert 'id="lyric-share"' in main and 'id="lyric-share"' in records, 'song links need a visible control in the lyrics header'
assert 'Copy link to “${track.title}”' in app_source, 'song-link control needs a title-specific accessible label'
assert 'copy song link' not in app_source.lower(), 'song-link control should not be buried in notes and credits'
assert 'class="round-play lyric-primary-play"' in app_source, 'direct song links need a prominent play control on the artwork'
assert 'Play “${track.title}” by ${track.artist}' in app_source, 'prominent play control needs a song-specific accessible name'
assert '.lyric-stage:not(.is-direct-entry) .lyric-primary-play' in experience_source, 'prominent play belongs only to the initial direct-link state'
assert '.lyric-stage[data-mode="peek"] .lyric-primary-play' in experience_source, 'compact lyrics must not gain a second play control'
assert main.index('id="unfortunately"') < main.index('id="counterfactual"'), '(unfortunately) must precede Revisionist History'
assert main.index('id="self-awareness"') < main.index('data-album-embed="unfortunately"'), 'the self-awareness argument belongs directly under the first album description'
assert main.index('id="self-awareness"') < main.index('id="counterfactual"'), 'the self-awareness argument belongs with (Unfortunately), not at the end'
assert main.index('id="victory-lap"') < main.index('class="postmodernism-thread"'), 'the postmodernism link should remain the closing coda'
assert 'class="intelligence-arc"' not in main, 'the abstract intelligence-arrow diagram should be removed'
assert 'class="self-awareness-listening"' in main, 'the album argument needs a visual, playable break'
assert 'assets/favicon-parenthetical.svg' in main and 'assets/favicon-parenthetical.svg' in records, 'both pages must use the self-awareness favicon'
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
