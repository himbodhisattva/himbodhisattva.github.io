import {VERSION, MANIFEST_SHA256} from './config.js';
import {createState, restoreState, startSubmission, applyOutcome, skipItem, postReview} from './state.js';

const querySet = new URLSearchParams(location.search).get('set');
const set = ['1', '2', '3'].includes(querySet) ? querySet : '1';
const endpoint = location.hostname === '192.168.0.58'
  ? 'http://192.168.0.58:4312/api/sound-reviews'
  : 'https://ivri-listening-review.samh.chatgpt.site/api/sound-reviews';
const key = `ivri-listening:${VERSION}:${MANIFEST_SHA256}`;
const app = document.querySelector('#app');
const progress = document.querySelector('#progress');
const escape = text => String(text).replace(/[&<>"']/g, c => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'}[c]));
const playIcon = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m8 4 12 8-12 8Z"/></svg>';
const pauseIcon = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 4v16M16 4v16"/></svg>';
let state;
let clips = [];
let activeAudio = null;
let saving = false;

function newSessionId() {
  const bytes = crypto.getRandomValues(new Uint8Array(16));
  bytes[6] = (bytes[6] & 15) | 64; bytes[8] = (bytes[8] & 63) | 128;
  const h = [...bytes].map(n => n.toString(16).padStart(2, '0')).join('');
  return `${h.slice(0,8)}-${h.slice(8,12)}-${h.slice(12,16)}-${h.slice(16,20)}-${h.slice(20)}`;
}

function storageWarning() { document.querySelector('#storage-warning').hidden = false; }
function persist() {
  try { localStorage.setItem(key, JSON.stringify(state)); } catch { storageWarning(); }
}
function stopAudio() {
  if (!activeAudio) return;
  const previous = activeAudio; activeAudio = null;
  previous.pause(); previous.removeAttribute('src'); previous.load();
}
function focusPage() {
  app.querySelector('h1')?.focus({preventScroll: true});
  window.scrollTo({top: 0, behavior: 'auto'});
}

function intro() {
  stopAudio(); progress.textContent = '4 sounds';
  app.innerHTML = `<section class="intro"><h1 tabindex="-1">Check four Hebrew sounds</h1><p>Listen, then tell us if each sound is correct. Modern Israeli pronunciation.</p></section>
    <form id="begin"><details class="profile-options"><summary>About you (optional)</summary><div class="profile">
      <label class="field"><span>Your Hebrew</span><select name="background"><option value="unspecified">Choose, or leave blank</option><option value="native">Native speaker</option><option value="fluent">Fluent speaker / reader</option><option value="teacher">Hebrew teacher</option><option value="learning">Still learning</option></select></label>
      <label class="field"><span>Name or nickname</span><input name="alias" maxlength="80" autocomplete="off"></label>
    </div></details><button class="primary">Start listening</button></form>`;
  app.querySelector('form').onsubmit = event => {
    event.preventDefault();
    state.profile = {background: event.target.elements.background.value, alias: event.target.elements.alias.value.trim()};
    persist(); showNext();
  };
  focusPage();
}

function showNext() {
  saving = false;
  const next = clips.find(clip => !['saved', 'savedElsewhere', 'skipped'].includes(state.items[clip.id]?.stage));
  if (next) review(next); else done();
}

function review(clip, message = '') {
  stopAudio();
  state.items[clip.id] ??= {stage: 'draft', answer: {heard: false, pronunciation: '', note: ''}};
  const item = state.items[clip.id];
  const answer = item.answer;
  const index = clips.indexOf(clip);
  const frozen = item.stage !== 'draft';
  persist(); progress.textContent = `${index + 1} of 4`;
  app.innerHTML = `<section><h1 tabindex="-1">Does this sound right?</h1>
    <div class="sound-prompt"><p class="hebrew" lang="he" dir="rtl" id="sound-target">${escape(clip.hebrew)}</p>
      <button class="player" type="button" aria-label="Play sound" aria-describedby="sound-target"><span class="play-icon">${playIcon}</span><span><span class="clip-label">Listen</span><small class="heard">${answer.heard ? 'Played' : ''}</small></span><span class="track"></span></button>
    </div>
    <form id="review"><fieldset><legend class="sr-only">Is the written syllable pronounced correctly, without extra sounds?</legend><div class="sound-choices">
      ${[['correct','Correct, no extra sounds'], ['incorrect','Something sounds wrong'], ['unsure','Not sure']].map(([value, label]) => `<label class="choice"><input type="radio" name="pronunciation" value="${value}" ${answer.pronunciation === value ? 'checked' : ''} ${frozen ? 'disabled' : ''}><span>${label}</span></label>`).join('')}
    </div></fieldset>
    <details ${answer.note ? 'open' : ''}><summary>Add a note (optional)</summary><label class="field"><span>What sounds wrong or unclear?</span><textarea name="note" maxlength="1000" dir="auto" ${frozen ? 'disabled' : ''}>${escape(answer.note)}</textarea></label></details>
    <p class="status" role="status" aria-live="polite">${escape(message || (item.stage === 'pending' ? 'Your previous answer still needs confirmation. Retry to save it.' : ''))}</p>
    <div class="actions"><button class="primary" type="submit">${item.stage === 'pending' ? 'Retry saving' : index === 3 ? 'Send & finish' : 'Send & next'}</button><button class="text-button" id="skip" type="button" ${frozen ? 'disabled' : ''}>Skip this sound</button></div></form></section>`;
  const form = app.querySelector('form');
  const status = app.querySelector('.status');
  const player = app.querySelector('.player');
  const audio = new Audio(clip.src); audio.preload = 'auto'; activeAudio = audio;
  const sync = () => {
    if (activeAudio !== audio) return;
    const playing = !audio.paused;
    player.dataset.playing = String(playing);
    player.querySelector('.play-icon').innerHTML = playing ? pauseIcon : playIcon;
    player.querySelector('.clip-label').textContent = playing ? 'Pause' : 'Listen again';
    player.setAttribute('aria-label', playing ? 'Pause sound' : 'Play sound');
  };
  audio.addEventListener('play', sync); audio.addEventListener('pause', sync);
  audio.addEventListener('timeupdate', () => {
    if (activeAudio === audio) player.querySelector('.track').style.width = `${Number.isFinite(audio.duration) ? audio.currentTime / audio.duration * 100 : 0}%`;
  });
  audio.addEventListener('ended', () => {
    if (activeAudio !== audio) return;
    if (item.stage === 'draft') { answer.heard = true; persist(); }
    player.querySelector('.heard').textContent = 'Played'; sync();
  });
  audio.addEventListener('error', () => {
    if (activeAudio === audio) status.textContent = 'The sound didn’t load. Tap Listen to retry, or skip it.';
  });
  player.onclick = async () => {
    if (!audio.paused) { audio.pause(); return; }
    if (audio.error) audio.load();
    try {
      await audio.play();
      if (activeAudio === audio && item.stage === 'draft') status.textContent = '';
    } catch {
      if (activeAudio === audio) status.textContent = 'Audio could not start. Tap Listen to try again.';
    }
  };
  form.oninput = () => {
    if (item.stage !== 'draft' || saving) return;
    answer.pronunciation = form.elements.pronunciation.value; answer.note = form.elements.note.value; persist();
  };
  app.querySelector('#skip').onclick = () => {
    if (saving) return;
    skipItem(state, clip.id); persist(); showNext();
  };
  if (item.stage === 'conflict') {
    status.textContent = 'An answer for this sound was already saved from this browser. The first answer was kept.';
    const button = form.querySelector('.primary'); button.type = 'button'; button.textContent = 'Continue';
    button.onclick = () => {
      state.items[clip.id] = {stage: 'savedElsewhere', answer: {...answer}};
      persist(); showNext();
    };
  } else form.onsubmit = async event => {
    event.preventDefault(); if (saving) return;
    try { startSubmission(state, clip); } catch (error) { status.textContent = error.message; return; }
    persist(); saving = true; audio.pause();
    form.querySelectorAll('button,input,textarea').forEach(control => control.disabled = true);
    player.disabled = true; form.querySelector('.primary').textContent = 'Saving…'; status.textContent = '';
    const outcome = await postReview(endpoint, state.items[clip.id].body);
    applyOutcome(state, clip.id, outcome); persist(); saving = false;
    if (outcome === 'saved') showNext();
    else review(clip, outcome === 'invalid'
      ? 'This answer wasn’t accepted. Your draft is kept. You can retry or skip this sound.'
      : outcome === 'retry' ? 'We couldn’t confirm the save. Your answer is kept here. Check your connection and retry.' : '');
  };
  focusPage();
}

function done() {
  stopAudio(); progress.textContent = 'Finished';
  const saved = clips.filter(clip => ['saved', 'savedElsewhere'].includes(state.items[clip.id]?.stage)).length;
  const prior = clips.some(clip => state.items[clip.id]?.stage === 'savedElsewhere');
  const nextSets = ['1','2','3'].filter(value => value !== set &&
    !allClips.filter(clip => clip.set === value).every(clip => ['saved', 'savedElsewhere'].includes(state.items[clip.id]?.stage)));
  app.innerHTML = `<section class="done"><h1 tabindex="-1">${saved ? 'Thank you. That helps.' : 'Thanks for taking a look.'}</h1>
    <p>${saved === 4 ? 'All four answers are saved.' : `${saved} of 4 answers saved. Skipped sounds weren’t submitted.`}${prior ? ' Earlier answers from this browser were kept.' : ''}</p>
    ${saved < 4 ? '<button class="primary" id="revisit">Try skipped sounds</button>' : ''}
    ${nextSets.length ? `<nav class="done-nav" aria-label="Other sound sets">${nextSets.map(value => `<a href="?set=${value}">Four more sounds · Set ${value}</a>`).join('')}</nav>` : ''}</section>`;
  app.querySelector('#revisit')?.addEventListener('click', () => {
    for (const clip of clips) if (state.items[clip.id]?.stage === 'skipped') {
      state.items[clip.id] = {stage: 'draft', answer: {...state.items[clip.id].answer}};
    }
    persist(); showNext();
  });
  focusPage();
}

document.addEventListener('visibilitychange', () => { if (document.hidden) activeAudio?.pause(); });
window.addEventListener('pagehide', () => activeAudio?.pause());
let allClips;
try {
  const response = await fetch('clips.json');
  if (!response.ok) throw new Error('Missing manifest');
  const manifest = await response.json();
  if (manifest.version !== VERSION || manifest.clips?.length !== 12) throw new Error('Wrong manifest');
  allClips = manifest.clips; clips = allClips.filter(clip => clip.set === set);
  if (clips.length !== 4) throw new Error('Missing sound set');
  const sessionId = newSessionId();
  try { state = restoreState(localStorage.getItem(key), allClips, sessionId); }
  catch { state = createState(sessionId); storageWarning(); }
  persist(); app.setAttribute('aria-busy', 'false');
  if (state.profile) showNext(); else intro();
} catch {
  app.setAttribute('aria-busy', 'false');
  app.innerHTML = '<h1 tabindex="-1">Sounds didn’t load</h1><p>Check your connection and reload.</p><button class="primary" id="reload">Reload</button>';
  app.querySelector('#reload').onclick = () => location.reload();
}
