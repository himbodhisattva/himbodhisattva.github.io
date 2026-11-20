const get = (id) => document.getElementById(id);
const review = get('review');
const checkpoint = get('checkpoint');
const pause = get('break');
const download = get('download');
const note = get('note');
const play = get('play');
const alternate = get('alternate');
const status = get('playback-status');
const outcomes = [
  [get('approve'), 'approved', 'Sounds right'],
  [get('fix'), 'fix', 'Needs a fix'],
  [get('unsure'), 'unsure', 'Unsure'],
];

async function loadJson(path) {
  const response = await fetch(path);
  if (!response.ok) throw new Error(`Unavailable: ${path}`);
  return response.json();
}

async function start() {
  const [{ id, coreCount, groups }, { queueId, byGroup }] = await Promise.all([
    loadJson('queue.json'),
    loadJson('pronunciations.json'),
  ]);
  if (queueId !== id || groups.some(({ id: groupId }) => !byGroup?.[groupId])) {
    throw new Error('Pronunciations do not match the clips');
  }
  const storageKey = `ivri-listening-review:${id}`;
  const positions = [...groups.slice(0, coreCount), null, ...groups.slice(coreCount), null];
  let state = { position: 0, judgments: {} };
  let storageAvailable = true;
  try {
    const restored = JSON.parse(localStorage.getItem(storageKey));
    if (Number.isInteger(restored?.position) && restored.position >= 0 &&
        restored.position < positions.length && restored.judgments) {
      state = restored;
    }
  } catch {
    storageAvailable = false;
  }
  let current;
  let choice;
  let player;
  let heard;
  const saved = () => state.judgments[current.id];
  const hasResponses = () => Object.keys(state.judgments).length > 0;

  function updateStorage() {
    try {
      localStorage.setItem(storageKey, JSON.stringify(state));
    } catch {
      storageAvailable = false;
    }
    if (!storageAvailable) {
      get('save-status').textContent = 'This browser may lose progress. Download your review before closing this page.';
    }
    download.disabled = !hasResponses();
    get('finish').disabled = download.disabled;
  }

  function saveNote() {
    if (!current) return;
    const entry = saved();
    const draft = note.value.trim();
    if (!draft && !entry?.notes?.[choice]) return;
    state.judgments[current.id] ??= { clips: {}, notes: {} };
    if (draft) state.judgments[current.id].notes[choice] = draft;
    else delete state.judgments[current.id].notes[choice];
    updateStorage();
  }

  function focus(element) {
    element.focus({ preventScroll: true });
  }

  function stopPlayer() {
    player?.pause();
    player = undefined;
  }

  function syncControls() {
    const verdict = saved()?.clips[choice]?.verdict;
    for (const [button, value, label] of outcomes) {
      button.disabled = !heard.has(choice);
      button.setAttribute('aria-pressed', String(value === verdict));
      button.textContent = label;
    }
    const label = choice === current.primary ? 'Play' : 'Play alternate';
    play.textContent = player && !player.paused ? 'Pause' : heard.has(choice) ? 'Replay ' + (choice === current.primary ? 'clip' : 'alternate') : label;
    alternate.hidden = !current.alternate;
    alternate.textContent = choice === current.primary ? 'Try alternate' : 'Back to first clip';
    status.textContent = verdict
      ? `Saved · ${outcomes.find(([, value]) => value === verdict)[2]}`
      : heard.has(choice) ? '' : 'Play the whole clip to rate it.';
  }

  function select(sha256) {
    stopPlayer();
    choice = sha256;
    note.value = saved()?.notes?.[choice] ?? '';
    get('notes').open = Boolean(note.value);
    syncControls();
  }

  function render(moveFocus = true) {
    stopPlayer();
    current = positions[state.position];
    review.hidden = !current;
    pause.hidden = Boolean(current);
    const reviewed = Object.values(state.judgments).filter((entry) => Object.keys(entry.clips).length > 0).length;
    if (!current) {
      const finished = state.position === positions.length - 1;
      checkpoint.textContent = '';
      get('break-title').textContent = finished ? 'You reached the end' : 'End of the opening set';
      get('break-copy').textContent = `${reviewed} clips rated. Download your review to send it back.`;
      get('continue').hidden = finished;
      if (moveFocus) focus(get('break-title'));
      return;
    }
    const inCore = state.position < coreCount;
    const count = inCore ? coreCount : groups.length - coreCount;
    const number = inCore ? state.position + 1 : state.position - coreCount;
    get('lesson').textContent = current.lesson;
    get('position').textContent = `${number} / ${count}`;
    get('progress').max = count;
    get('progress').value = number - 1;
    get('hebrew').textContent = current.text;
    get('pronunciation').textContent = byGroup[current.id];
    checkpoint.textContent = inCore ? '' : 'More Hebrew Reading and Prayers';
    get('back').disabled = state.position === 0;
    get('skip').textContent = saved()?.clips[current.primary] || saved()?.clips[current.alternate] ? 'Next' : 'Skip';
    heard = new Set();
    const ratings = saved()?.clips ?? {};
    const approved = Object.entries(ratings).find(([, rating]) => rating.verdict === 'approved');
    const needsAlternate = current.alternate && ratings[current.primary] && !ratings[current.alternate];
    select(approved?.[0] ?? (needsAlternate ? current.alternate : current.primary));
    if (moveFocus) focus(play);
  }

  function move(step) {
    saveNote();
    state.position += step;
    updateStorage();
    render();
  }

  async function togglePlayback() {
    if (player && !player.paused) {
      player.pause();
      syncControls();
      return;
    }
    if (!player || player.ended || player.error) {
      const track = new Audio(`audio/${choice}.mp3`);
      player = track;
      track.addEventListener('ended', () => {
        if (player !== track) return;
        const played = track.played;
        if (Number.isFinite(track.duration) && played.length === 1 &&
            played.start(0) < .05 && played.end(0) >= track.duration - .05) {
          heard.add(choice);
        }
        syncControls();
      });
      track.addEventListener('pause', () => {
        if (player === track && !track.ended) syncControls();
      });
      track.addEventListener('error', () => {
        if (player !== track) return;
        syncControls();
        status.textContent = 'Clip unavailable. Tap Play to retry.';
      });
    }
    const track = player;
    try {
      await track.play();
      if (player === track) syncControls();
    } catch {
      if (player === track) status.textContent = 'Couldn’t play the clip. Tap Play to retry.';
    }
  }

  function rate(verdict) {
    if (!heard.has(choice)) return;
    saveNote();
    const entry = state.judgments[current.id] ??= { clips: {}, notes: {} };
    if (verdict === 'approved') {
      for (const hash of Object.keys(entry.clips)) {
        if (entry.clips[hash].verdict === 'approved') delete entry.clips[hash];
      }
    }
    entry.clips[choice] = { verdict, reviewedAt: new Date().toISOString() };
    delete entry.skipped;
    updateStorage();
    const other = choice === current.primary ? current.alternate : current.primary;
    if (verdict !== 'approved' && other && !entry.clips[other]) {
      select(other);
      status.textContent = 'There’s another recording to try.';
      focus(play);
    } else {
      move(1);
    }
  }

  function exportReview() {
    const items = {};
    for (const group of groups) {
      const entry = state.judgments[group.id];
      const selected = Object.entries(entry?.clips ?? {}).find(([, rating]) => rating.verdict === 'approved');
      if (!selected) continue;
      const [sha256, { reviewedAt }] = selected;
      for (const { itemId, ...binding } of group.targets) {
        items[itemId] = { ...binding, sha256, reviewedAt, method: 'listened-v1' };
      }
    }
    const output = { schemaVersion: 1, queueId: id, items, judgments: state.judgments };
    const url = URL.createObjectURL(new Blob([JSON.stringify(output, null, 2) + '\n'], { type: 'application/json' }));
    const link = document.createElement('a');
    link.href = url;
    link.download = 'ivri-listening-review.json';
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 30_000);
    get('save-status').textContent = 'Send ivri-listening-review.json back to the person who shared this link.';
  }

  play.addEventListener('click', togglePlayback);
  alternate.addEventListener('click', () => {
    saveNote();
    select(choice === current.primary ? current.alternate : current.primary);
    focus(play);
  });
  for (const [button, verdict] of outcomes) button.addEventListener('click', () => rate(verdict));
  note.addEventListener('input', saveNote);
  get('skip').addEventListener('click', () => {
    const entry = state.judgments[current.id] ??= { clips: {}, notes: {} };
    if (Object.keys(entry.clips).length === 0) entry.skipped = true;
    move(1);
  });
  get('back').addEventListener('click', () => move(-1));
  get('return').addEventListener('click', () => move(-1));
  get('continue').addEventListener('click', () => move(1));
  get('finish').addEventListener('click', exportReview);
  download.addEventListener('click', exportReview);
  updateStorage();
  render(false);
}

start().catch(() => {
  checkpoint.textContent = 'The clips couldn’t load. Reload the page to try again.';
});
