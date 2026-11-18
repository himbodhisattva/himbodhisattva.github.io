import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import test from 'node:test';
import {VERSION, MANIFEST_SHA256} from '../ivri-listen/sounds/config.js';
import {createState, restoreState, startSubmission, applyOutcome, skipItem, postReview} from '../ivri-listen/sounds/state.js';

const manifestBytes = readFileSync(new URL('../ivri-listen/sounds/clips.json', import.meta.url));
const manifest = JSON.parse(manifestBytes);
const clip = manifest.clips[0];
const sessionId = '7c6be2dd-9f7f-4088-a67d-f9c67fa1b0ca';
function answered() {
  const state = createState(sessionId);
  state.profile = {background: 'fluent', alias: 'QA synthetic'};
  state.items[clip.id] = {stage: 'draft', answer: {heard: true, pronunciation: 'incorrect', note: 'Synthetic workflow check'}};
  return state;
}

test('every delivered clip matches the frozen manifest and three four-item sets', () => {
  assert.equal(createHash('sha256').update(manifestBytes).digest('hex'), MANIFEST_SHA256);
  assert.equal(manifest.version, VERSION);
  assert.equal(new Set(manifest.clips.map(c => c.id)).size, 12);
  for (const set of ['1', '2', '3']) assert.equal(manifest.clips.filter(c => c.set === set).length, 4);
  for (const row of manifest.clips) {
    const bytes = readFileSync(new URL(`../ivri-listen/sounds/${row.src}`, import.meta.url));
    assert.equal(createHash('sha256').update(bytes).digest('hex'), row.audioSha256);
    assert.equal(bytes.length, row.bytes);
  }
});

test('a lost response survives reload and retries exactly the submitted payload', async () => {
  const state = answered();
  startSubmission(state, clip);
  const submitted = structuredClone(state.items[clip.id].body);
  assert.equal(submitted.manifestSha256, MANIFEST_SHA256);
  const requests = [];
  const offline = async (_url, init) => {requests.push(init); throw new Error('Lost response');};
  const result = await postReview('/api/sound-reviews', submitted, {fetcher: offline});
  assert.equal(result, 'retry');
  applyOutcome(state, clip.id, result);
  const restored = restoreState(JSON.stringify(state), manifest.clips, sessionId);
  startSubmission(restored, clip);
  assert.deepEqual(restored.items[clip.id].body, submitted);
  assert.throws(() => skipItem(restored, clip.id), /pending/);
  const saved = await postReview('/api/sound-reviews', restored.items[clip.id].body, {fetcher: async (_url, init) => {requests.push(init); return Response.json({saved: true});}});
  assert.equal(requests[0].body, requests[1].body);
  assert.equal(requests[1].credentials, 'omit');
  applyOutcome(restored, clip.id, saved);
  assert.equal(restored.items[clip.id].stage, 'saved');
});

test('a conflicting answer cannot overwrite the first answer and is distinct from success', async () => {
  const state = answered(); startSubmission(state, clip);
  const result = await postReview('/api/sound-reviews', state.items[clip.id].body, {fetcher: async () => Response.json({error: 'review_already_saved'}, {status: 409})});
  assert.equal(result, 'conflict');
  applyOutcome(state, clip.id, result);
  assert.equal(state.items[clip.id].stage, 'conflict');
  assert.throws(() => startSubmission(state, clip), /draft/);
});

test('uncertain server responses keep submissions pending; definite rejection reopens the draft', async () => {
  for (const response of [Response.json({saved: false}), Response.json({}, {status: 503}), Response.json({}, {status: 429}), new Response('broken')]) {
    assert.equal(await postReview('/api/sound-reviews', {}, {fetcher: async () => response}), 'retry');
  }
  const state = answered(); startSubmission(state, clip);
  const result = await postReview('/api/sound-reviews', state.items[clip.id].body, {fetcher: async () => Response.json({error: 'invalid_review'}, {status: 400})});
  applyOutcome(state, clip.id, result);
  assert.equal(state.items[clip.id].stage, 'draft');
  assert.equal(state.items[clip.id].answer.note, 'Synthetic workflow check');
  assert.equal('body' in state.items[clip.id], false);
});

test('submission requires completed playback and a judgment; skipped items never submit', () => {
  const state = answered();
  state.items[clip.id].answer.heard = false;
  assert.throws(() => startSubmission(state, clip), /Listen/);
  state.items[clip.id].answer.heard = true;
  state.items[clip.id].answer.pronunciation = '';
  assert.throws(() => startSubmission(state, clip), /Choose/);
  skipItem(state, clip.id);
  assert.throws(() => startSubmission(state, clip), /draft/);
});

test('corrupt, stale and cross-manifest drafts cannot become responses to current clips', () => {
  for (const raw of ['{', 'null', '{}', JSON.stringify({...answered(), manifestSha256: 'old'}), JSON.stringify({...answered(), version: 'old'})]) {
    assert.deepEqual(restoreState(raw, manifest.clips, sessionId), createState(sessionId));
  }
  const state = answered(); startSubmission(state, clip);
  state.items[clip.id].body.itemId = manifest.clips[1].id;
  assert.equal(restoreState(JSON.stringify(state), manifest.clips, sessionId).items[clip.id], undefined);
});

test('a stalled save has a bounded deadline', async () => {
  const result = await postReview('/api/sound-reviews', {}, {timeoutMs: 5, fetcher: (_url, {signal}) => new Promise((_resolve, reject) => signal.addEventListener('abort', () => reject(new Error('aborted')), {once: true}))});
  assert.equal(result, 'retry');
});
