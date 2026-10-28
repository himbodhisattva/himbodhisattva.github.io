import assert from 'node:assert/strict';

globalThis.window = {};
await import('../player-model.js');
const { nextPlayable, activeCueIndex, buildQueueContext, routePath, escapeLayer } = window.ANS_PLAYER_MODEL;

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
assert.equal(escapeLayer(true, true), 'dialog', 'Escape closes the topmost dialog first');
assert.equal(escapeLayer(false, true), 'lyrics');
assert.equal(escapeLayer(false, false), null);

console.log('PASS: explicit album queues and lyric cue lookup.');
