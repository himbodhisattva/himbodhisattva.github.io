#!/usr/bin/env python3
"""Dependency-free catalog, route and source checks. Run browser tests separately."""
from pathlib import Path
import re,json,sys
ROOT=Path(__file__).resolve().parent.parent
text=(ROOT/'data.js').read_text();data=json.loads(re.sub(r'^window\.ANS_DATA\s*=\s*','',text).rstrip().removesuffix(';'))
ids=[x['id'] for x in data['tracks']]
assert len(ids)==len(set(ids)), 'duplicate track IDs'
assert len(data['tracks'])==49 and len(data['albums'])==7
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
assert album_by_id['my-art-machine']['tracks']==['my-art-machine-01'], 'My Art Machine must remain a one-song album'
assert album_by_id['my-art-machine']['art']=='assets/user/my-art-machine-1254.webp', 'My Art Machine must use its full-resolution cover'
assert track_by_id['revisionist-02']['title']=='Like They Do In The Movies (a new sincerity remix)', 'Movies share title changed unexpectedly'
assert track_by_id['revisionist-02']['art']=='assets/movies.webp', 'Movies share link must use its own artwork'
assert track_by_id['friday-girls-05']['art']=='assets/user/friday-girls-again-and-again.webp', 'Again and Again must use its track artwork'
assert track_by_id['my-art-machine-01']['originalUrl']=='https://suno.com/song/53914ce6-b9a6-4341-9e44-14c438a5ca91', 'My Art Machine must retain its canonical Suno source'
assert all(manifest['albums'][a['id']]['art']==a['art'] for a in data['albums']), 'album artwork paths disagree with the media manifest'
assert all(manifest['tracks'][t['id']]['art']==t['art'] and manifest['tracks'][t['id']]['audio']==t['audio'] for t in data['tracks']), 'track media paths disagree with the media manifest'
assert all(t['group']==album_by_id[t['album']]['group'] for t in data['tracks']), 'track and album groups disagree'
assert data['defaultTrack']=='my-art-machine-01', 'The untouched player should begin with the homepage release'
assert data['queue'][0]=='my-art-machine-01', 'The story queue should begin with the homepage release'
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
social_images={
 documents[0]:'https://himbodhisattva.com/a-new-sincerity/assets/user/my-art-machine-1254.webp',
 documents[1]:'https://himbodhisattva.com/a-new-sincerity/assets/user/victory-lap-1254.webp',
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
 assert f'<meta property="og:image" content="{social_images[document]}">' in html
 assert f'<meta name="twitter:image" content="{social_images[document]}">' in html
 assert '<meta name="twitter:card" content="summary_large_image">' in html
 for path in re.findall(r'(?:src|href)="(assets/[^\"]+)"',html):assert (ROOT/path).is_file(),path
main=documents[0].read_text()
records=documents[1].read_text()
public_copy=(main+records).lower()
main_markup=re.search(r'<main>(.*?)</main>',main,re.S).group(1)
main_prose_blocks=re.findall(r'<(?:p|blockquote)(?:\s[^>]*)?>(.*?)</(?:p|blockquote)>',main_markup,re.S)
main_prose=' '.join(re.sub(r'<[^>]+>',' ',block) for block in main_prose_blocks)
main_prose_word_count=len(re.findall(r"\b[\w’'-]+\b",main_prose))
assert 300<=main_prose_word_count<=450, f'homepage prose should add narrative without returning to the 820-word explainer, found {main_prose_word_count} words'
release_hero=re.search(r'<section class="release-hero".*?</section>',main_markup,re.S).group()
assert main_markup.index(release_hero) < main_markup.index('id="about-project"'), 'the homepage must open with the release'
assert release_hero.index('class="art-button release-hero-art"') < release_hero.index('class="release-hero-copy"'), 'release artwork should lead the hero in reading order'
assert main_markup.index('data-play="my-art-machine-01"') < main_markup.index('id="about-project"'), 'visitors should reach a playable song before project explanation'
assert main_markup.count('class="philosophy-trigger"')==1, 'the homepage should keep exactly one quiet path to the long philosophy note'
assert 'my art machine has the right aesthetics' in main_markup.lower()
assert "that's how you know i'm so authentic" in main_markup.lower()
assert "the songs aren't the art" not in main_markup.lower(), 'the old thesis should not lead the release page'
for stale_surface in ('class="reading-line"', 'class="album-theory"', 'class="chapter-rail"', 'class="postmodernism-thread"'):
 assert stale_surface not in main, f'old explainer surface remains: {stale_surface}'
assert main_markup.count('class="release-card"')>=5, 'the homepage should foreground at least five release covers'
assert len(re.findall(r'<button\b[^>]*\bdata-play=',main_markup))>=5, 'the homepage should expose at least five immediate play controls'
for lyric_fragment in (
 'every crack is intentional',
 "and i don't want a medal",
 'but da da does it mean anything at all?',
 'wait, you like me too?!',
 'i made the whole thing up',
 'but god, does this sound good tonight.',
):
 assert lyric_fragment in main_markup.lower(), f'missing original lyric voice: {lyric_fragment}'
assert 'Seven records and forty-nine tracks' in records, 'records metadata must match the seven-album, forty-nine-track catalog'
assert 'Seven records, forty-nine tracks' in records, 'records share description must match the current catalog'
assert '<details' not in main and '<summary' not in main, 'homepage should avoid stacked accordions'
assert 'Minima' not in main_markup and 'minima' not in main_markup, 'Minima should remain in the catalog, not the homepage focus'
assert 'Like They Do In The Movies' in main_markup
assert 'somehow both a victory lap and a cry for help' in main_markup.lower()
assert 'emulated stereogum' in main_markup.lower()
assert 'simulated reviews' not in main_markup.lower(), 'review terminology must stay emulated'
assert 'data-play="victory-lap-01"' in main_markup
assert 'id="art-machine"' in main_markup, 'Art Machine needs its own shareable homepage section'
assert 'href="records/my-art-machine/"' in release_hero, 'the Art Machine cover should open its one-song album'
assert 'src="assets/user/my-art-machine-1254.webp"' in release_hero, 'the Art Machine section should use its full-resolution cover'
art_machine_play=re.search(r'<button[^>]+data-play="my-art-machine-01"[^>]*>',release_hero).group()
assert 'data-queue="album"' in art_machine_play and 'data-album-context="my-art-machine"' in art_machine_play, 'Art Machine playback should retain its one-song album context'
for album_id in ('unfortunately', 'revisionist', 'friday-girls'):
 assert f'data-album-embed="{album_id}"' in main_markup, f'{album_id} should retain its playable track list'
assert main_markup.index('data-album-context="unfortunately"') < main_markup.index('class="release-note release-note-dark"') < main_markup.index('data-album-embed="unfortunately"'), 'Unfortunately context should follow its Play control and precede its track list'
assert main_markup.index('data-album-context="revisionist"') < main_markup.index('class="release-note release-note-history"') < main_markup.index('data-album-embed="revisionist"'), 'Revisionist context should follow its Play control and precede its track list'
assert main_markup.index('data-album-context="friday-girls"') < main_markup.index('class="friday-story"') < main_markup.index('data-album-embed="friday-girls"'), 'Friday Girls context should follow its Play control and precede its track list'
assert main_markup.index('class="review-bridge"') < main_markup.index('id="victory-lap"'), 'the emulated review should lead into the song it named'
for album_id in ('unfortunately', 'revisionist', 'friday-girls', 'victory-lap'):
 assert f'href="records/{album_id}/"' in main_markup, f'{album_id} cover should open its static record page'
assert 'records/#album=' not in main_markup, 'homepage album links must be crawler-visible paths'
assert 'AI reconstruction from a recording where the original performance is barely audible' in main_markup, 'Movies needs the provenance that explains why both versions are reconstructions'
for narrative_turn in (
 'what would counterfactual me be writing if i\'d kept making pop-punk?',
 'the narrator is me when i\'m chasing praise for being self-aware',
 'then i gave counterfactual me the songs i had already written.',
 'friday girls sit outside the self-awareness thing.',
 'the fake band is part of my daughters\' actual childhood now.',
 "who's the real one now?",
):
 assert narrative_turn in main_markup.lower(), f'missing release narrative: {narrative_turn}'
assert 'The Narrator would also like credit for recognizing this.' not in main_markup
assert 'The Protagonist' not in main_markup
assert 'keep going' not in main_markup
assert 'class="old-song-note"' not in main_markup
assert 'class="feedback-loop"' not in main_markup
assert 'class="intelligence-arc"' not in main_markup
assert 'the creation changed its creator' not in main_markup.lower()
assert 'the map modifies the territory' not in main_markup.lower()
assert 'view the post on X' not in main_markup, 'narrated X source links should be removed'
assert 'class="twitter-tweet"' not in main_markup, 'release page should not embed X widgets'
assert 'platform.twitter.com/widgets.js' not in main
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
assert 'individual songs record intermediate states' in main.lower(), 'the medium strand should identify the evolving process as the artwork'
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
 assert cut_copy not in main_markup, f'cut copy remains: {cut_copy}'
app_source=(ROOT/'app.js').read_text()
experience_source=(ROOT/'experience.css').read_text()
player_model_source=(ROOT/'player-model.js').read_text()
assert 'album page' not in app_source.lower(), 'story track lists should rely on their clickable album covers'
assert 'open the album' not in main.lower(), 'album covers should carry record navigation without an instruction label'
assert 'openPhilosophy({ returnFocus: null });' in app_source, 'direct philosophy links must not restore focus to an off-screen trigger'
assert 'openPhilosophy({ returnFocus: event.currentTarget });' in app_source, 'click-opened philosophy notes should restore focus to the activating link'
assert "document.querySelectorAll('.philosophy-trigger')" in app_source, 'every philosophy link must be bound, not only the first one'
for page in (main, records):
    assert 'data.js?v=20261030e' in page
    assert 'style.css?v=20261030e' in page
    assert 'experience.css?v=20261030e' in page
    assert 'player-model.js?v=20261030e' in page
    assert 'app.js?v=20261030e' in page
    assert not any(version in page for version in ('20261030a', '20261030b', '20261030c', '20261030d')), 'stale asset cache key remains'
    assert '<a href="https://suno.com/">Suno v6-pro</a>' in page
assert '↗' not in (main+records+app_source), 'decorative up-right arrows remain'
assert 'id="liner-notes"' not in main and 'review-centerpiece' not in main and 'current-status' not in main
assert 'attached' not in (main+records+app_source).lower(), 'stale attachment copy remains'
assert 'id="records"' in main, 'the homepage should expose a scrollable release sequence'
assert 'id="records"' in records and 'id="album-stage"' in records
assert 'id="lyric-stage"' in main and 'id="lyric-stage"' in records
assert 'id="lyric-share"' in main and 'id="lyric-share"' in records, 'song links need a visible control in the lyrics header'
assert 'Copy link to “${track.title}”' in app_source, 'song-link control needs a title-specific accessible label'
assert 'copy song link' not in app_source.lower(), 'song-link control should not be buried in notes and credits'
share_track_source=re.search(r'async function shareTrack\(id\) \{.*?\n  \}',app_source,re.S).group()
route_source=re.search(r'async function route\(\) \{.*?\n  \}',app_source,re.S).group()
open_lyrics_source=re.search(r'async function openLyrics\(id,.*?\n  \}',app_source,re.S).group()
assert 'recordRoutePath' in player_model_source, 'player model must expose canonical album and song paths'
assert 'recordRouteId' in player_model_source, 'player model must recognize generated record paths'
assert 'model.recordRoutePath' in share_track_source, 'shared song links must use the canonical static route'
assert '.hash' not in share_track_source and '#track=' not in share_track_source, 'shared song links must not use crawler-invisible fragments'
assert 'model.recordRouteId' in route_source, 'generated record paths must dispatch by catalog membership'
assert 'openLyrics' in route_source, 'generated song paths must open the full inner sleeve'
assert 'albums.has(recordRoute)' in route_source, 'generated album paths must open their matching album'
assert 'href="${escape(albumUrl(album.id).href)}"' in app_source, 'record shelf covers must expose copyable static album links'
assert 'selectTrack(id, { play: false' in open_lyrics_source, 'direct song routes must arrive paused'
assert 'class="round-play lyric-primary-play"' in app_source, 'direct song links need a prominent play control on the artwork'
assert 'Play “${track.title}” by ${track.artist}' in app_source, 'prominent play control needs a song-specific accessible name'
assert '.lyric-stage:not(.is-direct-entry) .lyric-primary-play' in experience_source, 'prominent play belongs only to the initial direct-link state'
assert '.lyric-stage[data-mode="peek"] .lyric-primary-play' in experience_source, 'compact lyrics must not gain a second play control'
assert main_markup.index('id="art-machine"') < main_markup.index('id="about-project"') < main_markup.index('id="unfortunately"'), 'the release should lead, followed by one short artist note and the records'
assert main_markup.index('id="unfortunately"') < main_markup.index('id="counterfactual"') < main_markup.index('id="friday-girls"') < main_markup.index('id="victory-lap"'), 'featured releases should retain their intended sequence'
assert 'assets/favicon-parenthetical.svg' in main and 'assets/favicon-parenthetical.svg' in records, 'both pages must use the self-awareness favicon'
for recommendation in ('our favorite', 'start with', 'places to start', 'save this one for later', 'funniest song'):
 assert recommendation not in public_copy, f'recommendation copy remains: {recommendation}'
records_hero=re.search(r'<header class="records-hero">(.*?)</header>',records,re.S).group(1)
assert re.sub(r'<[^>]+>','',records_hero).strip()=='the records.', 'records page hero should say only “the records.”'
sync_text=(ROOT/'lyrics-sync.js').read_text()
sync=json.loads(re.sub(r'^window\.ANS_SYNC\s*=\s*','',sync_text).rstrip().removesuffix(';'))
my_art_cues=sync['my-art-machine-01']['cues']
my_art_lines=[line for line in track_by_id['my-art-machine-01']['lyrics'].splitlines() if line.strip()]
assert len(my_art_cues)==len(my_art_lines)+2, 'My Art Machine must include the final two-line refrain performed twice in the recording'
assert [cue['text'].lower() for cue in my_art_cues[-4:]]==[line.lower() for line in my_art_lines[-2:]]*2, 'My Art Machine repeated refrain drifted from the performed take'
assert my_art_cues[0]['start'] < 2 and my_art_cues[-2]['start'] < 150, 'My Art Machine lyric timing drifted away from the recording'
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
print('PASS: catalog ownership, release-first homepage, standalone records route, player sources, cue maps and staging visibility.')
