/* A New Sincerity: one player for the essay, records room and timed inner sleeve. */
(() => {
  'use strict';

  const D = window.ANS_DATA;
  const model = window.ANS_PLAYER_MODEL;
  if (!D || !model) return;

  const tracks = new Map(D.tracks.map(track => [track.id, track]));
  const albums = new Map(D.albums.map(album => [album.id, album]));
  const audio = document.getElementById('audio');
  const dialog = document.getElementById('detail-dialog');
  const dialogContent = document.getElementById('dialog-content');
  const lyricStage = document.getElementById('lyric-stage');
  const philosophyDialog = document.getElementById('philosophy-dialog');
  const philosophyTrigger = document.querySelector('.philosophy-trigger');
  const recordsPage = document.body.dataset.page === 'records';
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const defaultAlbumId = D.albums[0]?.id || 'unfortunately';

  const state = {
    current: null,
    queue: model.buildQueueContext('story', 'essay', D.queue),
    filter: 'all',
    query: '',
    selectedAlbum: defaultAlbumId,
    lyricCues: [],
    activeCue: -1,
    lyricMode: 'closed',
    followLyrics: true,
    lyricReturnFocus: null,
    dialogReturnFocus: null,
    philosophyReturnFocus: null,
    lyricHistoryEntry: false,
    recovering: false,
  };

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));
  const escape = value => String(value ?? '').replace(/[&<>"']/g, character => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  })[character]);
  const asset = path => path ? (window.ANS_ASSETS?.[path] || path) : '';
  const source = track => asset(track.audio);
  const artFor = track => asset(track.art || albums.get(track.album)?.art);
  const albumArt = album => asset(album.art);
  const canPlay = id => Boolean(tracks.get(id)?.audio);

  function emptyPlayerAction(action) {
    return model.emptyPlayerAction(action, {
      recordsPage,
      selectedAlbum: state.selectedAlbum,
      albums: D.albums,
      defaultTrack: D.defaultTrack,
      storyQueue: D.queue,
    }, canPlay);
  }

  function setLyricsMode(mode) {
    const open = mode !== 'closed';
    const full = mode === 'full';
    state.lyricMode = mode;
    lyricStage.dataset.mode = mode;
    lyricStage.hidden = !open;
    $('#lyrics-close').setAttribute('aria-label', model.lyricCloseLabel(mode));
    document.body.classList.toggle('lyrics-open', full);
    $$('body > .skip-link, body > header, body > main').forEach(element => { element.inert = full; });
  }

  const iconPaths = {
    play: '<path d="m8 5 11 7-11 7Z" fill="currentColor" stroke="none"/>',
    pause: '<path d="M8 5v14M16 5v14" stroke-width="4"/>',
    close: '<path d="m6 6 12 12M18 6 6 18"/>',
    next: '<path d="m5 5 10 7-10 7Z" fill="currentColor" stroke="none"/><path d="M19 5v14"/>',
    previous: '<path d="m19 5-10 7 10 7Z" fill="currentColor" stroke="none"/><path d="M5 5v14"/>',
    search: '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>',
    volume: '<path d="M4 9h4l5-4v14l-5-4H4Z"/><path d="M16 8c3 2 3 6 0 8M19 5c5 4 5 10 0 14"/>',
    muted: '<path d="M4 9h4l5-4v14l-5-4H4Z"/><path d="m17 9 5 6m0-6-5 6"/>',
    share: '<path d="M12 15V3m-5 5 5-5 5 5M7 12H4v9h16v-9h-3"/>',
  };

  function icon(name) {
    return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${iconPaths[name] || iconPaths.play}</svg>`;
  }

  $$('[data-icon]').forEach(element => { element.innerHTML = icon(element.dataset.icon); });

  function announce(message) {
    const status = $('#player-status');
    if (status) status.textContent = message;
  }

  let toastTimer;
  function toast(message) {
    const element = $('#toast');
    if (!element) return;
    clearTimeout(toastTimer);
    element.textContent = message;
    element.classList.add('show');
    toastTimer = setTimeout(() => element.classList.remove('show'), 4200);
  }

  function resetPhilosophyScroll() {
    if (!philosophyDialog) return;
    philosophyDialog.scrollTop = 0;
    requestAnimationFrame(() => {
      philosophyDialog.scrollTop = 0;
      setTimeout(() => { philosophyDialog.scrollTop = 0; }, 0);
    });
  }

  function openPhilosophy({ returnFocus = null } = {}) {
    if (!philosophyDialog || philosophyDialog.open) return;
    state.philosophyReturnFocus = returnFocus?.isConnected ? returnFocus : null;
    if (dialog.open) dialog.close();
    philosophyDialog.showModal();
    resetPhilosophyScroll();
  }

  function closePhilosophy({ updateHistory = true, restoreFocus = true } = {}) {
    if (!philosophyDialog?.open) return;
    const returnFocus = state.philosophyReturnFocus || $('.site-wordmark');
    philosophyDialog.close();
    philosophyDialog.scrollTop = 0;
    if (updateHistory && location.hash === '#philosophy') {
      if (history.state?.ansPhilosophy) history.back();
      else history.replaceState(history.state, '', `${location.pathname}${location.search}`);
    }
    if (restoreFocus && returnFocus?.isConnected) requestAnimationFrame(() => returnFocus.focus({ preventScroll: true }));
  }

  function fmt(seconds) {
    return Number.isFinite(seconds) && seconds >= 0
      ? `${Math.floor(seconds / 60)}:${String(Math.floor(seconds % 60)).padStart(2, '0')}`
      : '—:—';
  }

  function artMarkup(album) {
    const image = albumArt(album);
    if (image) return `<img src="${escape(image)}" alt="${escape(album.title)} — album artwork" loading="lazy" width="1080" height="1080">`;
    return `<span class="placeholder-cover cover-${escape(album.id)}"><span class="cover-artist">${escape(album.artist)}</span><span class="cover-title">${escape(album.title)}</span></span>`;
  }

  function miniArt(track, className = 'track-art') {
    const image = artFor(track);
    return `<span class="${className}" aria-hidden="true">${image ? `<img src="${escape(image)}" alt="" width="100" height="100" loading="lazy">` : '<span>♫</span>'}</span>`;
  }

  function feature(track) {
    const sleeveLabel = track.instrumental ? 'Open track sleeve' : 'Open timed lyrics';
    return `<div class="track-feature">${miniArt(track)}<div class="track-copy"><strong>${escape(track.title.toLowerCase())}</strong><small>${escape(track.artist)}</small></div><div class="track-actions"><button class="text-button" data-lyrics="${track.id}" data-album-context="${track.album}" aria-label="${sleeveLabel} for ${escape(track.title)}">${track.instrumental ? 'sleeve' : 'lyrics'}</button><button class="round-play" data-play="${track.id}" data-queue="album" data-album-context="${track.album}" aria-label="Play ${escape(track.title)}">${icon('play')}</button></div></div>`;
  }

  function refreshFeatures() {
    $$('[data-track-card]').forEach(element => {
      const track = tracks.get(element.dataset.trackCard);
      if (track) element.innerHTML = feature(track);
    });
    $$('[data-album-cover]').forEach(element => {
      const album = albums.get(element.dataset.albumCover);
      const image = album && albumArt(album);
      if (!image) return;
      element.innerHTML = `<img src="${escape(image)}" alt="${escape(album.title)} album artwork" width="1080" height="1080">`;
      element.classList.remove('typographic-cover', 'fg-cover');
      element.classList.add('art-button');
    });
    $$('[data-album-embed]').forEach(element => {
      const album = albums.get(element.dataset.albumEmbed);
      if (!album) return;
      element.innerHTML = `<div class="story-album-head"><span>${quantity(album.tracks.length, 'track')}</span></div><ol class="track-list story-track-list">${album.tracks.map(id => trackRow(tracks.get(id))).join('')}</ol>`;
      element.setAttribute('aria-label', `${album.title} track list`);
    });
    syncPlayButtons();
  }

  function trackRow(track, number = track.number) {
    return `<li class="track-row" data-track-id="${track.id}"><span class="track-index">${String(number).padStart(2, '0')}</span><div class="track-info"><button class="track-title-button" data-lyrics="${track.id}" data-album-context="${track.album}">${escape(track.title.toLowerCase())}</button><small>${escape(track.artist)}</small></div><button class="text-button" data-lyrics="${track.id}" data-album-context="${track.album}" aria-label="${track.instrumental ? 'Open track sleeve' : 'Open timed lyrics'} for ${escape(track.title)}">${track.instrumental ? 'sleeve' : 'lyrics'}</button><button class="round-play" data-play="${track.id}" data-queue="album" data-album-context="${track.album}" aria-label="Play ${escape(track.title)}">${icon('play')}</button></li>`;
  }

  const quantity = (count, singular, plural = `${singular}s`) => `${count} ${count === 1 ? singular : plural}`;

  function albumShelfItem(album) {
    const selected = album.id === state.selectedAlbum;
    return `<button class="album-open${selected ? ' is-selected' : ''}" data-album="${album.id}" aria-pressed="${selected}" aria-label="Show ${escape(album.title)} by ${escape(album.artist)}"><span class="album-cover">${artMarkup(album)}</span><span class="album-meta"><span>${escape(album.artist)}</span><span>${quantity(album.tracks.length, 'track')}</span></span><strong>${escape(album.title.toLowerCase())}</strong></button>`;
  }

  function renderAlbumStage(albumId, updateHistory = false) {
    const stage = $('#album-stage');
    const album = albums.get(albumId);
    if (!stage || !album) return;
    state.selectedAlbum = albumId;
    stage.innerHTML = `<div class="album-stage-art"><div class="album-cover">${artMarkup(album)}</div><p>${escape(album.credit)}</p></div><div class="album-stage-copy"><p class="eyebrow">${escape(album.artist)} · ${quantity(album.tracks.length, 'track')}</p><h2 tabindex="-1">${escape(album.title.toLowerCase())}</h2><p class="album-description">${escape(album.description)}</p><button class="button primary" data-play-album="${album.id}">${icon('play')} play album</button><ul class="track-list">${album.tracks.map(id => trackRow(tracks.get(id))).join('')}</ul></div>`;
    $$('.album-open').forEach(button => {
      const selected = button.dataset.album === albumId;
      button.classList.toggle('is-selected', selected);
      button.setAttribute('aria-pressed', String(selected));
    });
    syncPlayButtons();
    if (updateHistory && recordsPage) {
      const target = model.routePath(location.pathname, location.search, 'album', albumId);
      if (`${location.pathname}${location.search}${location.hash}` !== target) history.pushState({ ansAlbum: albumId }, '', target);
    }
  }

  function revealAlbumStage({ userSelection = false, directLink = false } = {}) {
    const stage = $('#album-stage');
    const behavior = model.albumScrollBehavior({ userSelection, directLink, reducedMotion: reducedMotion.matches });
    if (!stage || !behavior) return;
    requestAnimationFrame(() => {
      stage.scrollIntoView({ behavior, block: 'start' });
      if (userSelection) stage.querySelector('h2')?.focus({ preventScroll: true });
    });
  }

  function decodeRouteId(value) {
    try { return decodeURIComponent(value); } catch { return null; }
  }

  function renderRecords() {
    const grid = $('#album-grid');
    if (!grid) return;
    const filteredAlbums = D.albums.filter(album => state.filter === 'all' || album.group === state.filter);
    const query = state.query.trim().toLocaleLowerCase();
    const results = $('#search-results');
    const count = $('#library-count');
    grid.hidden = Boolean(query);
    results.hidden = !query;

    if (query) {
      const hits = D.tracks.filter(track => (state.filter === 'all' || track.group === state.filter)
        && `${track.title} ${track.artist} ${albums.get(track.album).title}`.toLocaleLowerCase().includes(query));
      results.innerHTML = hits.length ? `<ul class="track-list search-track-list">${hits.map(track => trackRow(track)).join('')}</ul>` : '<p class="empty-results">No song, artist, or record matches that search.</p>';
      count.textContent = `${hits.length} matching ${hits.length === 1 ? 'song' : 'songs'}`;
    } else {
      grid.innerHTML = filteredAlbums.map(albumShelfItem).join('');
      const trackCount = filteredAlbums.reduce((total, album) => total + album.tracks.length, 0);
      count.textContent = `${quantity(filteredAlbums.length, 'record')} · ${quantity(trackCount, 'track')}`;
      if (!filteredAlbums.some(album => album.id === state.selectedAlbum) && filteredAlbums[0]) {
        state.selectedAlbum = filteredAlbums[0].id;
      }
      renderAlbumStage(state.selectedAlbum);
    }
    syncPlayButtons();
  }

  function queueForButton(button, track) {
    if (button.dataset.queue === 'story') return model.buildQueueContext('story', 'essay', D.queue);
    const albumId = button.dataset.albumContext || track.album;
    const album = albums.get(albumId);
    return model.buildQueueContext('album', albumId, album?.tracks || [track.id]);
  }

  async function selectTrack(id, { play = true, queue = null, automatic = false } = {}) {
    const track = tracks.get(id);
    if (!track) return;
    if (queue) state.queue = queue;

    const src = source(track);
    if (state.current !== id) {
      audio.pause();
      audio.removeAttribute('src');
      audio.load();
      state.current = id;
      state.activeCue = -1;
    }
    if (!src) {
      toast('The recording is unavailable in this browser.');
      return;
    }
    if (audio.getAttribute('src') !== src) {
      audio.src = src;
      audio.load();
    }
    updatePlayer();
    if (!play) return;
    try {
      await audio.play();
      const lyricEvent = model.playbackLyricEvent({ automatic });
      const mode = model.nextLyricMode(state.lyricMode, lyricEvent, true);
      if (mode !== 'closed') {
        const historyAction = model.lyricRouteAction('track-change', { mode: state.lyricMode });
        showLyrics(track, { mode, historyAction });
      }
      announce(`playing ${track.title} by ${track.artist}`);
    } catch (error) {
      if (error.name !== 'AbortError') {
        toast('This recording could not play.');
        announce('Playback failed.');
      }
    }
    updatePlayer();
  }

  async function toggleCurrent() {
    if (!state.current) {
      const initial = emptyPlayerAction('play');
      if (initial) await selectTrack(initial.track, { queue: initial.queue });
      return;
    }
    if (audio.paused) await selectTrack(state.current);
    else audio.pause();
  }

  async function advance(direction, wrap, { automatic = false } = {}) {
    if (!state.current) {
      const initial = emptyPlayerAction(direction < 0 ? 'previous' : 'next');
      if (!initial) return false;
      await selectTrack(initial.track, { queue: initial.queue });
      return true;
    }
    if (direction < 0 && audio.currentTime > 3) {
      audio.currentTime = 0;
      return true;
    }
    const next = model.nextPlayable(state.queue, state.current, direction, canPlay, wrap);
    if (!next) return false;
    await selectTrack(next, { queue: state.queue, automatic });
    return true;
  }

  function syncPlayButtons() {
    $$('button[data-play]').forEach(button => {
      const active = state.current === button.dataset.play && !audio.paused;
      const iconNode = button.classList.contains('round-play') ? button : button.querySelector('.icon');
      if (iconNode) iconNode.innerHTML = icon(active ? 'pause' : 'play');
      button.classList.toggle('is-playing', active);
      button.setAttribute('aria-label', `${active ? 'Pause' : 'Play'} ${tracks.get(button.dataset.play)?.title || 'recording'}`);
    });
    const toggle = $('#play-pause');
    if (toggle) {
      toggle.innerHTML = icon(audio.paused ? 'play' : 'pause');
      toggle.setAttribute('aria-label', audio.paused ? 'Play' : 'Pause');
    }
  }

  function updatePlayer() {
    const track = tracks.get(state.current);
    if (track) {
      $('#player-title').textContent = track.title.toLowerCase();
      $('#player-artist').textContent = `${track.artist} · ${albums.get(track.album).title}`;
      const image = artFor(track);
      $('#player-art').innerHTML = image ? `<img src="${escape(image)}" alt="" width="48" height="48">` : '<span aria-hidden="true">♫</span>';
      if ('mediaSession' in navigator) {
        try {
          navigator.mediaSession.metadata = new MediaMetadata({
            title: track.title,
            artist: track.artist,
            album: albums.get(track.album).title,
            artwork: image ? [{ src: image, sizes: '1080x1080' }] : [],
          });
        } catch {}
      }
      if (state.lyricMode !== 'closed' && $('#lyric-title').dataset.track !== track.id) renderLyrics(track);
    }
    syncPlayButtons();
    updateTime();
  }

  function updateTime() {
    const valid = Number.isFinite(audio.duration) && audio.duration > 0;
    $('#current-time').textContent = fmt(audio.currentTime || 0);
    $('#duration').textContent = valid ? fmt(audio.duration) : '—:—';
    $('#seek').disabled = !valid;
    $('#seek').value = valid ? String(Math.round(audio.currentTime / audio.duration * 1000)) : '0';
    $('#seek').setAttribute('aria-valuetext', valid ? `${fmt(audio.currentTime)} of ${fmt(audio.duration)}` : 'recording not loaded');
    $('#mobile-progress').style.width = valid ? `${audio.currentTime / audio.duration * 100}%` : '0';
    updateActiveLyrics();
  }

  function estimatedCues(track) {
    const rawLines = track.instrumental ? [] : track.lyrics.split('\n');
    const lines = [];
    let stanzaStart = true;
    for (const raw of rawLines) {
      const text = raw.trim();
      if (!text) {
        stanzaStart = true;
        continue;
      }
      lines.push({ text, stanzaStart, weight: Math.max(2, text.split(/\s+/).length) });
      stanzaStart = false;
    }
    const duration = track.duration || 180;
    const start = Math.min(8, duration * 0.06);
    const end = Math.max(start + 1, duration - Math.min(4, duration * 0.025));
    const total = lines.reduce((sum, line) => sum + line.weight, 0) || 1;
    let cursor = start;
    return lines.map((line, index) => {
      const lineDuration = (end - start) * line.weight / total;
      const cue = { start: cursor, end: index === lines.length - 1 ? duration : cursor + lineDuration, text: line.text, stanzaStart: line.stanzaStart, estimated: true };
      cursor += lineDuration;
      return cue;
    });
  }

  function cuesFor(track) {
    const exact = window.ANS_SYNC?.[track.id];
    if (exact?.cues?.length && Math.abs((exact.duration || track.duration) - track.duration) < 2) return exact.cues;
    return estimatedCues(track);
  }

  function renderLyrics(track) {
    const image = artFor(track);
    state.lyricCues = cuesFor(track);
    state.activeCue = -1;
    state.followLyrics = true;
    $('#lyric-title').textContent = track.title.toLowerCase();
    $('#lyric-title').dataset.track = track.id;
    $('#lyric-artist').textContent = `${track.artist} · ${albums.get(track.album).title}`;
    $('#lyric-art').innerHTML = image ? `<img src="${escape(image)}" alt="${escape(track.title)} artwork" width="1080" height="1080">` : '<span aria-hidden="true">♫</span>';
    $('#lyric-backdrop').style.backgroundImage = image ? `url("${String(image).replace(/["\\]/g, '\\$&')}")` : '';
    const lines = $('#lyric-lines');
    $('#lyric-stage-label').textContent = track.instrumental ? 'inner sleeve / instrumental' : 'inner sleeve / timed lyrics';
    lines.setAttribute('aria-label', track.instrumental ? 'Instrumental track sleeve' : 'Timed lyrics');
    if (track.instrumental) {
      lines.innerHTML = '<p class="instrumental-lyric">instrumental</p>';
    } else {
      lines.innerHTML = state.lyricCues.map((cue, index) => `<button class="lyric-line${cue.stanzaStart ? ' stanza-start' : ''}" data-cue="${index}" data-seek-time="${cue.start.toFixed(2)}"><span>${escape(cue.text)}</span></button>`).join('');
    }
    lines.scrollTop = 0;
    $('#lyric-follow').hidden = true;
    updateActiveLyrics(true);
  }

  function showLyrics(track, { mode = 'peek', historyAction = null, returnFocus = null, focus = false } = {}) {
    const wasClosed = state.lyricMode === 'closed';
    lyricStage.dataset.presentation = model.playPresentation(track);
    if ($('#lyric-title').dataset.track !== track.id) renderLyrics(track);
    else {
      state.followLyrics = true;
      $('#lyric-follow').hidden = true;
      updateActiveLyrics(true);
    }
    if (focus || (wasClosed && mode === 'peek')) state.lyricReturnFocus = returnFocus || document.activeElement;
    setLyricsMode(mode);
    updateActiveLyrics(true);
    if (focus) $('#lyric-lines').focus({ preventScroll: true });
    if (historyAction) {
      const url = new URL(location.href);
      url.hash = `track=${encodeURIComponent(track.id)}`;
      if (historyAction === 'replace' || state.lyricHistoryEntry) {
        history.replaceState(history.state, '', url);
      } else {
        history.pushState({ ansLyrics: true }, '', url);
        state.lyricHistoryEntry = true;
      }
    }
  }

  async function openLyrics(id, { updateHistory = true, returnFocus = null } = {}) {
    const track = tracks.get(id);
    if (!track) return;
    if (recordsPage && state.selectedAlbum !== track.album) renderAlbumStage(track.album);
    else state.selectedAlbum = track.album;
    const queue = state.queue.kind === 'album' && state.queue.id === track.album
      ? state.queue
      : model.buildQueueContext('album', track.album, albums.get(track.album).tracks);
    await selectTrack(id, { play: false, queue });
    showLyrics(track, { mode: model.nextLyricMode(state.lyricMode, 'open', !audio.paused), historyAction: updateHistory ? 'open' : null, returnFocus, focus: true });
  }

  function closeLyrics({ updateHistory = true } = {}) {
    if (state.lyricMode === 'closed') return;
    const wasFull = state.lyricMode === 'full';
    const nextMode = model.nextLyricMode(state.lyricMode, 'close', !audio.paused);
    const returnTarget = state.lyricReturnFocus?.isConnected && state.lyricReturnFocus !== document.body
      ? state.lyricReturnFocus
      : $('#player-lyrics');
    const routeAction = updateHistory
      ? model.lyricRouteAction('close', { ownsEntry: state.lyricHistoryEntry, hash: location.hash })
      : null;
    setLyricsMode(nextMode);
    if (routeAction === 'back') {
      state.lyricHistoryEntry = false;
      if (history.state?.ansLyrics) history.back();
      else {
        const destination = recordsPage && state.selectedAlbum
          ? model.routePath(location.pathname, location.search, 'album', state.selectedAlbum)
          : `${location.pathname}${location.search}`;
        history.replaceState(null, '', destination);
      }
    } else if (routeAction === 'replace') {
      state.lyricHistoryEntry = false;
      const destination = recordsPage && state.selectedAlbum
        ? model.routePath(location.pathname, location.search, 'album', state.selectedAlbum)
        : `${location.pathname}${location.search}`;
      history.replaceState(null, '', destination);
    }
    if (!updateHistory) state.lyricHistoryEntry = false;
    if ((wasFull || nextMode === 'closed') && returnTarget?.isConnected) returnTarget.focus({ preventScroll: true });
    state.lyricReturnFocus = nextMode === 'peek' ? returnTarget : null;
  }

  function updateActiveLyrics(force = false) {
    if (state.lyricMode === 'closed' || !state.lyricCues.length) return;
    const index = model.activeCueIndex(state.lyricCues, audio.currentTime || 0);
    if (!force && index === state.activeCue) return;
    state.activeCue = index;
    $$('.lyric-line', lyricStage).forEach((line, lineIndex) => {
      line.classList.toggle('is-active', lineIndex === index);
      line.classList.toggle('is-past', lineIndex < index);
      line.setAttribute('aria-current', lineIndex === index ? 'true' : 'false');
    });
    if (state.followLyrics && index >= 0) {
      const active = $(`.lyric-line[data-cue="${index}"]`, lyricStage);
      const lines = $('#lyric-lines');
      if (active) {
        const top = active.offsetTop - (lines.clientHeight - active.offsetHeight) / 2;
        lines.scrollTo({ top: Math.max(0, top), behavior: reducedMotion.matches ? 'auto' : 'smooth' });
      }
    }
  }

  function pauseLyricFollow() {
    if (state.lyricMode === 'closed' || !state.lyricCues.length) return;
    state.followLyrics = false;
    $('#lyric-follow').hidden = false;
  }

  function showDialog(kicker, html) {
    $('#dialog-kicker').textContent = kicker;
    dialogContent.innerHTML = html;
    if (!dialog.open) {
      state.dialogReturnFocus = document.activeElement;
      dialog.showModal();
    }
    dialog.scrollTop = 0;
  }

  function openNotes(id) {
    const track = tracks.get(id);
    if (!track) return;
    const album = albums.get(track.album);
    const lyricsSource = track.source.replace(/\.md$/i, '');
    showDialog('notes & credits', `<div class="dialog-main"><div class="detail-track-head">${miniArt(track, 'detail-art')}<div><p class="eyebrow">${escape(track.artist)}</p><h2 id="dialog-title">${escape(track.title.toLowerCase())}</h2></div></div><p>${escape(track.note || album.description)}</p><p><strong>record:</strong> ${escape(album.title)}<br><strong>artist:</strong> ${escape(track.artist)}<br><strong>lyrics source:</strong> ${escape(lyricsSource)}<br><strong>how this version was made:</strong> ${escape(track.provenance)}</p><div class="detail-actions"><button class="button primary" data-lyrics="${track.id}" data-album-context="${track.album}">${track.instrumental ? 'open sleeve' : 'timed lyrics'}</button><button class="text-button" data-share="${track.id}">copy song link</button><a class="text-button" href="${escape(source(track))}" download>download audio</a></div></div>`);
  }

  function openArtwork(button) {
    showDialog('the artwork', `<div class="art-view"><h2 id="dialog-title" class="sr-only">${escape(button.dataset.artLabel)}</h2><img src="${escape(asset(button.dataset.art))}" alt="${escape(button.dataset.artLabel)}"><p>${escape(button.dataset.artLabel)}</p></div>`);
  }

  async function shareTrack(id) {
    const track = tracks.get(id);
    if (!track) return;
    const url = new URL('records/', document.baseURI);
    url.hash = `track=${encodeURIComponent(id)}`;
    try {
      await navigator.clipboard.writeText(url.href);
      toast('song link copied');
    } catch {
      showDialog('song link', `<div class="dialog-main"><p class="eyebrow">copy this address</p><h2 id="dialog-title">song link</h2><p class="copy-url">${escape(url.href)}</p></div>`);
    }
  }

  function updateReadingProgress() {
    const indicator = $('#reading-progress');
    if (!indicator) return;
    const maximum = document.documentElement.scrollHeight - innerHeight;
    indicator.style.width = maximum > 0 ? `${Math.min(100, scrollY / maximum * 100)}%` : '0';
  }

  async function route() {
    const trackMatch = location.hash.match(/^#track=(.+)$/);
    const albumMatch = location.hash.match(/^#album=(.+)$/);
    const philosophyRoute = !recordsPage && location.hash === '#philosophy';
    if (philosophyRoute) {
      if (state.lyricMode === 'full') closeLyrics({ updateHistory: false });
      openPhilosophy({ returnFocus: null });
      return;
    }
    if (philosophyDialog?.open) closePhilosophy({ updateHistory: false, restoreFocus: false });
    if (trackMatch) {
      const id = decodeRouteId(trackMatch[1]);
      if (tracks.has(id)) {
        state.lyricHistoryEntry = Boolean(history.state?.ansLyrics);
        await openLyrics(id, { updateHistory: false });
      } else {
        closeLyrics({ updateHistory: false });
        const stage = $('#album-stage');
        if (recordsPage && !stage?.childElementCount) renderAlbumStage(state.selectedAlbum);
      }
    } else {
      if (state.lyricMode === 'full') closeLyrics({ updateHistory: false });
      if (recordsPage) {
        const id = albumMatch ? decodeRouteId(albumMatch[1]) : defaultAlbumId;
        const stage = $('#album-stage');
        if (albums.has(id) && (state.selectedAlbum !== id || !stage?.childElementCount)) renderAlbumStage(id);
        if (albumMatch && albums.has(id)) revealAlbumStage({ directLink: true });
      }
    }
  }

  philosophyTrigger?.addEventListener('click', event => {
    if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    if (location.hash !== '#philosophy') history.pushState({ ansPhilosophy: true }, '', '#philosophy');
    openPhilosophy({ returnFocus: event.currentTarget });
  });

  document.addEventListener('click', async event => {
    const button = event.target.closest('button');
    if (!button) return;

    if (button.classList.contains('close-dialog')) {
      dialog.close();
      return;
    }
    if (button.id === 'philosophy-close') {
      closePhilosophy();
      return;
    }
    if (button.dataset.play) {
      const track = tracks.get(button.dataset.play);
      if (!track) return;
      const queue = queueForButton(button, track);
      if (state.current === track.id && !audio.paused) {
        state.queue = queue;
        audio.pause();
      } else await selectTrack(track.id, { queue });
      return;
    }
    if (button.dataset.lyrics) {
      const returnFocus = dialog.open ? state.dialogReturnFocus : null;
      if (dialog.open) dialog.close();
      await openLyrics(button.dataset.lyrics, { returnFocus });
      return;
    }
    if (button.dataset.notes) {
      openNotes(button.dataset.notes);
      return;
    }
    if (button.dataset.album) {
      renderAlbumStage(button.dataset.album, true);
      revealAlbumStage({ userSelection: true });
      return;
    }
    if (button.dataset.playAlbum) {
      const album = albums.get(button.dataset.playAlbum);
      const first = album.tracks.find(canPlay);
      if (first) await selectTrack(first, { queue: model.buildQueueContext('album', album.id, album.tracks) });
      return;
    }
    if (button.dataset.filter) {
      state.filter = button.dataset.filter;
      $$('[data-filter]').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
      renderRecords();
      return;
    }
    if (button.dataset.art) {
      openArtwork(button);
      return;
    }
    if (button.dataset.share) {
      await shareTrack(button.dataset.share);
      return;
    }
    if (button.dataset.seekTime) {
      audio.currentTime = Number(button.dataset.seekTime);
      state.followLyrics = true;
      $('#lyric-follow').hidden = true;
      if (audio.paused) await audio.play().catch(() => {});
      updateActiveLyrics(true);
      return;
    }
    if (button.id === 'play-pause') await toggleCurrent();
    else if (button.id === 'previous-track') await advance(-1, true);
    else if (button.id === 'next-track') await advance(1, true);
    else if (button.id === 'player-lyrics' || button.id === 'player-art') {
      const target = state.current
        ? { track: state.current, queue: state.queue }
        : emptyPlayerAction('lyrics');
      if (target) {
        state.queue = target.queue;
        await openLyrics(target.track);
      }
    }
    else if (button.id === 'lyrics-close') closeLyrics();
    else if (button.id === 'lyric-follow') {
      state.followLyrics = true;
      button.hidden = true;
      updateActiveLyrics(true);
    } else if (button.id === 'lyric-notes' && state.current) {
      openNotes(state.current);
    } else if (button.id === 'mute') {
      audio.muted = !audio.muted;
      button.innerHTML = icon(audio.muted ? 'muted' : 'volume');
      button.setAttribute('aria-label', audio.muted ? 'Unmute' : 'Mute');
    }
  });

  $('#library-search')?.addEventListener('input', event => {
    state.query = event.target.value;
    renderRecords();
  });
  $('#seek').addEventListener('input', event => {
    if (Number.isFinite(audio.duration)) audio.currentTime = audio.duration * Number(event.target.value) / 1000;
    updateTime();
  });
  $('#lyric-lines').addEventListener('wheel', pauseLyricFollow, { passive: true });
  $('#lyric-lines').addEventListener('touchmove', pauseLyricFollow, { passive: true });
  $('#lyric-lines').addEventListener('pointerdown', pauseLyricFollow, { passive: true });
  $('#lyric-lines').addEventListener('keydown', event => {
    if (['ArrowUp', 'ArrowDown', 'PageUp', 'PageDown', 'Home', 'End'].includes(event.key)) pauseLyricFollow();
  });

  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') {
      if (philosophyDialog?.open) {
        event.preventDefault();
        closePhilosophy();
        return;
      }
      const layer = model.escapeLayer(dialog.open, state.lyricMode !== 'closed');
      if (layer === 'dialog') {
        event.preventDefault();
        dialog.close();
        return;
      }
      if (layer === 'lyrics') {
        closeLyrics();
        return;
      }
    }
    if (event.code === 'Space' && state.lyricMode !== 'full' && !dialog.open && !philosophyDialog?.open && !event.target.closest('input,textarea,select,button,a,[contenteditable]')) {
      event.preventDefault();
      toggleCurrent();
    }
  });

  dialog.addEventListener('close', () => {
    if (state.dialogReturnFocus?.isConnected) state.dialogReturnFocus.focus({ preventScroll: true });
  });
  dialog.addEventListener('click', event => {
    if (event.target !== dialog) return;
    const bounds = dialog.getBoundingClientRect();
    if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
  });
  philosophyDialog?.addEventListener('cancel', event => {
    event.preventDefault();
    closePhilosophy();
  });
  philosophyDialog?.addEventListener('click', event => {
    if (event.target !== philosophyDialog) return;
    const bounds = philosophyDialog.getBoundingClientRect();
    if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) closePhilosophy();
  });

  audio.addEventListener('play', updatePlayer);
  ['pause', 'loadedmetadata', 'durationchange'].forEach(name => audio.addEventListener(name, updatePlayer));
  audio.addEventListener('timeupdate', updateTime);
  audio.addEventListener('ended', () => advance(1, false, { automatic: true }));
  audio.addEventListener('error', async () => {
    if (!audio.getAttribute('src') || state.recovering) return;
    state.recovering = true;
    const moved = await advance(1, false, { automatic: true });
    toast(moved ? 'This track could not load. Skipping to the next song.' : 'This track could not load.');
    state.recovering = false;
  });

  if ('mediaSession' in navigator) {
    const handlers = {
      play: () => toggleCurrent(),
      pause: () => audio.pause(),
      previoustrack: () => advance(-1, true),
      nexttrack: () => advance(1, true),
      seekto: details => { if (Number.isFinite(details.seekTime)) audio.currentTime = details.seekTime; },
    };
    for (const [name, handler] of Object.entries(handlers)) {
      try { navigator.mediaSession.setActionHandler(name, handler); } catch {}
    }
  }

  let progressScheduled = false;
  addEventListener('scroll', () => {
    if (progressScheduled) return;
    progressScheduled = true;
    requestAnimationFrame(() => {
      progressScheduled = false;
      updateReadingProgress();
    });
  }, { passive: true });
  addEventListener('resize', updateReadingProgress);
  let routeScheduled = false;
  function scheduleRoute() {
    if (routeScheduled) return;
    routeScheduled = true;
    queueMicrotask(() => {
      routeScheduled = false;
      route();
    });
  }
  addEventListener('popstate', scheduleRoute);
  addEventListener('hashchange', scheduleRoute);
  addEventListener('pageshow', event => {
    if (location.hash === '#philosophy') resetPhilosophyScroll();
    const navigation = performance.getEntriesByType?.('navigation')[0];
    if (event.persisted || navigation?.type !== 'reload') return;
    const albumMatch = location.hash.match(/^#album=(.+)$/);
    const id = albumMatch ? decodeRouteId(albumMatch[1]) : null;
    if (recordsPage && albums.has(id)) revealAlbumStage({ directLink: true });
  });

  if ('IntersectionObserver' in window) {
    const chapters = $$('[data-chapter]');
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        $$('.chapter-rail nav a').forEach(link => link.classList.toggle('active', link.getAttribute('href') === `#${entry.target.id}`));
      }
    }, { rootMargin: '-15% 0px -65% 0px' });
    chapters.forEach(chapter => observer.observe(chapter));
  }

  refreshFeatures();
  renderRecords();
  updatePlayer();
  updateReadingProgress();
  route();
})();
