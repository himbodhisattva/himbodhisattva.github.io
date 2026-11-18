import {VERSION, MANIFEST_SHA256} from './config.js';

const judgments = new Set(['correct', 'incorrect', 'unsure']);
const backgrounds = new Set(['native', 'fluent', 'teacher', 'learning', 'unspecified']);
const stages = new Set(['draft', 'pending', 'conflict', 'saved', 'savedElsewhere', 'skipped']);
const uuid = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

export function createState(sessionId) {
  return {version: VERSION, manifestSha256: MANIFEST_SHA256, sessionId, profile: null, items: {}};
}

function validAnswer(answer) {
  return answer && typeof answer.heard === 'boolean' &&
    (answer.pronunciation === '' || judgments.has(answer.pronunciation)) &&
    typeof answer.note === 'string' && answer.note.length <= 1000;
}

function bodyFor(state, clip, answer) {
  return {schemaVersion: 1, reviewVersion: VERSION, manifestSha256: MANIFEST_SHA256,
    sessionId: state.sessionId, set: clip.set, itemId: clip.id,
    pronunciation: answer.pronunciation, heard: true, note: answer.note,
    alias: state.profile.alias, background: state.profile.background};
}

export function restoreState(raw, clips, fallbackSessionId) {
  const fallback = createState(fallbackSessionId);
  let value;
  try { value = JSON.parse(raw); } catch { return fallback; }
  if (!value || value.version !== VERSION || value.manifestSha256 !== MANIFEST_SHA256 ||
      !uuid.test(value.sessionId) || !value.items || typeof value.items !== 'object') return fallback;
  if (value.profile !== null && (!value.profile || !backgrounds.has(value.profile.background) ||
      typeof value.profile.alias !== 'string' || value.profile.alias.length > 80)) return fallback;
  const state = {...fallback, sessionId: value.sessionId, profile: value.profile};
  for (const clip of clips) {
    const item = value.items[clip.id];
    if (!item || !stages.has(item.stage) || !validAnswer(item.answer)) continue;
    const answer = {heard: item.answer.heard, pronunciation: item.answer.pronunciation, note: item.answer.note};
    if (['pending', 'conflict'].includes(item.stage)) {
      if (!state.profile || !answer.heard || !judgments.has(answer.pronunciation) ||
          JSON.stringify(item.body) !== JSON.stringify(bodyFor(state, clip, answer))) continue;
      state.items[clip.id] = {stage: item.stage, answer, body: structuredClone(item.body)};
    } else {
      state.items[clip.id] = {stage: item.stage, answer};
    }
  }
  return state;
}

export function startSubmission(state, clip) {
  const item = state.items[clip.id];
  if (item?.stage === 'pending') return;
  if (item?.stage !== 'draft') throw new Error('Only a draft can be submitted.');
  if (!item.answer.heard) throw new Error('Listen to the sound first, or skip it.');
  if (!judgments.has(item.answer.pronunciation)) throw new Error('Choose an answer. “Not sure” is fine.');
  if (!state.profile) throw new Error('Start the review first.');
  state.items[clip.id] = {stage: 'pending', answer: {...item.answer}, body: bodyFor(state, clip, item.answer)};
}

export function applyOutcome(state, id, outcome) {
  const item = state.items[id];
  if (item?.stage !== 'pending') throw new Error('No pending answer to confirm.');
  if (outcome === 'retry') return;
  if (outcome === 'conflict') state.items[id] = {...item, stage: 'conflict'};
  else if (outcome === 'saved' || outcome === 'invalid') {
    state.items[id] = {stage: outcome === 'saved' ? 'saved' : 'draft', answer: {...item.answer}};
  } else throw new Error('Unknown save outcome.');
}

export function skipItem(state, id) {
  const item = state.items[id];
  if (item?.stage !== 'draft') throw new Error('A pending or completed answer cannot be skipped.');
  state.items[id] = {stage: 'skipped', answer: {...item.answer}};
}

export async function postReview(endpoint, body, {fetcher = fetch, timeoutMs = 12000} = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetcher(endpoint, {method: 'POST', headers: {'Content-Type': 'application/json'},
      credentials: 'omit', body: JSON.stringify(body), signal: controller.signal});
    if (response.status === 409) return 'conflict';
    if ([400, 403, 404, 413, 415, 422].includes(response.status)) return 'invalid';
    if (!response.ok) return 'retry';
    return (await response.json()).saved === true ? 'saved' : 'retry';
  } catch { return 'retry'; }
  finally { clearTimeout(timer); }
}
