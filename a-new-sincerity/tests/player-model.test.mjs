import assert from 'node:assert/strict';

globalThis.window = {};
await import('../player-model.js');
const {
  nextPlayable,
  activeCueIndex,
  buildQueueContext,
  routePath,
  escapeLayer,
  playPresentation,
  playbackLyricEvent,
  nextLyricMode,
  lyricRouteAction,
  lyricCloseLabel,
  albumScrollBehavior,
  initialPlayback,
  emptyPlayerAction,
  songRouteId,
  songRoutePath,
} = window.ANS_PLAYER_MODEL;

const available = new Set(['album-01', 'album-02', 'album-04']);
const canPlay = id => available.has(id);
const album = buildQueueContext('album', 'album', ['album-01', 'album-02', 'album-03', 'album-04']);

assert.equal(nextPlayable(album, 'album-01', 1, canPlay, false), 'album-02');
assert.equal(nextPlayable(album, 'album-02', 1, canPlay, false), 'album-04', 'unavailable middle tracks are skipped');
assert.equal(nextPlayable(album, 'album-04', 1, canPlay, false), null, 'natural album completion does not wrap');
assert.equal(nextPlayable(album, 'album-04', 1, canPlay, true), 'album-01', 'manual next may wrap');
assert.equal(nextPlayable(album, 'album-01', -1, canPlay, true), 'album-04');

const cues = [
  { start: 3.5, end: 8.1, text: 'first line' },
  { start: 8.1, end: 14.0, text: 'second line' },
  { start: 14.0, end: 19.0, text: 'third line' },
];
assert.equal(activeCueIndex(cues, 0), -1);
assert.equal(activeCueIndex(cues, 3.5), 0);
assert.equal(activeCueIndex(cues, 10), 1);
assert.equal(activeCueIndex(cues, 30), 2);

assert.deepEqual(buildQueueContext('story', 'essay', ['a', 'b']), {
  kind: 'story',
  id: 'essay',
  tracks: ['a', 'b'],
});

assert.equal(routePath('/records/', '', 'album', 'revisionist'), '/records/#album=revisionist');
assert.equal(
  routePath('/a-new-sincerity/records/', '?from=site', 'track', 'song & one'),
  '/a-new-sincerity/records/?from=site#track=song%20%26%20one',
);
assert.equal(
  songRouteId(
    '/a-new-sincerity/records/revisionist-02/',
    '/a-new-sincerity/records/',
  ),
  'revisionist-02',
  'a generated song path identifies the track to open',
);
assert.equal(
  songRouteId('/a-new-sincerity/records/', '/a-new-sincerity/records/'),
  null,
  'the records index is not mistaken for a song',
);
assert.equal(
  songRouteId(
    '/a-new-sincerity/records/revisionist-02/extra/',
    '/a-new-sincerity/records/',
  ),
  null,
  'only one path segment may identify a song',
);
assert.equal(
  songRoutePath('/a-new-sincerity/records/', 'revisionist-02'),
  '/a-new-sincerity/records/revisionist-02/',
  'shared song links use a crawlable path instead of a fragment',
);
assert.equal(
  songRoutePath('/a-new-sincerity/records/', 'song & one'),
  '/a-new-sincerity/records/song%20%26%20one/',
  'song paths encode route identifiers',
);
assert.equal(escapeLayer(true, true), 'dialog', 'Escape closes the topmost dialog first');
assert.equal(escapeLayer(false, true), 'lyrics');
assert.equal(escapeLayer(false, false), null);
assert.equal(playPresentation({ instrumental: false }), 'lyrics', 'playing a vocal track reveals timed lyrics');
assert.equal(playPresentation({ instrumental: true }), 'sleeve', 'playing an instrumental reveals its sleeve');
assert.equal(playbackLyricEvent({ automatic: true }), 'autoplay', 'queue continuation does not impersonate a new play request');
assert.equal(playbackLyricEvent({ automatic: false }), 'play', 'a listener-requested track may reveal lyrics');
assert.equal(nextLyricMode('closed', 'play', true), 'peek', 'play opens the compact lyric panel');
assert.equal(nextLyricMode('closed', 'autoplay', true), 'closed', 'autoplay respects a listener-closed lyric panel');
assert.equal(nextLyricMode('peek', 'autoplay', true), 'peek', 'autoplay keeps an open lyric panel following the queue');
assert.equal(nextLyricMode('peek', 'open', true), 'full', 'the lyrics control expands the panel');
assert.equal(
  nextLyricMode('closed', 'open', false),
  'full',
  'a direct song route opens the full sleeve while playback remains paused',
);
assert.equal(nextLyricMode('full', 'close', true), 'peek', 'closing full lyrics returns to the playing peek');
assert.equal(nextLyricMode('peek', 'close', true), 'closed', 'closing the peek hides it');
assert.equal(nextLyricMode('full', 'close', false), 'closed', 'paused full lyrics close completely');
assert.equal(lyricRouteAction('track-change', { mode: 'full' }), 'replace', 'full lyrics follow the active track URL');
assert.equal(lyricRouteAction('track-change', { mode: 'peek' }), null, 'compact lyrics do not add a track URL');
assert.equal(lyricRouteAction('close', { ownsEntry: true, hash: '#track=one' }), 'back', 'an internally opened track returns through history');
assert.equal(lyricRouteAction('close', { ownsEntry: false, hash: '#track=one' }), 'replace', 'a direct track link clears when closed');
assert.equal(lyricRouteAction('close', { directTrack: true }), 'replace', 'a static song route clears when closed');
assert.equal(lyricRouteAction('close', { ownsEntry: false, hash: '#album=one' }), null);
assert.equal(lyricCloseLabel('full'), 'Collapse lyrics');
assert.equal(lyricCloseLabel('peek'), 'Close lyrics');
assert.equal(albumScrollBehavior({ userSelection: true, reducedMotion: false }), 'smooth', 'choosing an album reveals its detail');
assert.equal(albumScrollBehavior({ directLink: true, reducedMotion: false }), 'smooth', 'direct album links reveal their detail');
assert.equal(albumScrollBehavior({ userSelection: true, reducedMotion: true }), 'auto', 'reduced motion avoids smooth scrolling');
assert.equal(albumScrollBehavior({}), null, 'initial catalog rendering does not move the page');

assert.deepEqual(
  initialPlayback({
    recordsPage: true,
    selectedAlbum: 'album-b',
    albums: [
      { id: 'album-a', tracks: ['album-01'] },
      { id: 'album-b', tracks: ['album-03', 'album-04'] },
    ],
    defaultTrack: 'album-01',
    storyQueue: ['album-01', 'album-02'],
  }, canPlay),
  {
    track: 'album-04',
    queue: { kind: 'album', id: 'album-b', tracks: ['album-03', 'album-04'] },
  },
  'empty player starts at the first playable track of the selected record',
);

assert.deepEqual(
  initialPlayback({
    recordsPage: false,
    selectedAlbum: 'album-b',
    albums: [{ id: 'album-b', tracks: ['album-04'] }],
    defaultTrack: 'album-02',
    storyQueue: ['album-01', 'album-02'],
  }, canPlay),
  {
    track: 'album-01',
    queue: { kind: 'story', id: 'essay', tracks: ['album-01', 'album-02'] },
  },
  'an untouched essay player starts with the first playable track at the top',
);

const emptyRecordsContext = {
  recordsPage: true,
  selectedAlbum: 'album-b',
  albums: [
    { id: 'album-a', tracks: ['album-01'] },
    { id: 'album-b', tracks: ['album-03', 'album-04'] },
  ],
  defaultTrack: 'album-01',
  storyQueue: ['album-01', 'album-02'],
};
for (const action of ['play', 'next', 'previous', 'lyrics']) {
  assert.deepEqual(
    emptyPlayerAction(action, emptyRecordsContext, canPlay),
    {
      action,
      track: 'album-04',
      queue: { kind: 'album', id: 'album-b', tracks: ['album-03', 'album-04'] },
    },
    `empty-player ${action} resolves against the selected record`,
  );
}

console.log('PASS: explicit album queues and lyric cue lookup.');
