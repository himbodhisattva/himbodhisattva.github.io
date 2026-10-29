/* Pure queue and lyric-cue helpers shared by the browser and Node tests. */
((root) => {
  'use strict';

  function buildQueueContext(kind, id, tracks) {
    return { kind, id, tracks: Array.from(tracks) };
  }

  function nextPlayable(context, current, direction, canPlay, wrap) {
    const playable = context.tracks.filter(canPlay);
    if (!playable.length) return null;

    const currentIndex = playable.indexOf(current);
    if (currentIndex < 0) return direction < 0 ? playable.at(-1) : playable[0];

    const candidate = currentIndex + direction;
    if (candidate >= 0 && candidate < playable.length) return playable[candidate];
    if (!wrap) return null;
    return direction < 0 ? playable.at(-1) : playable[0];
  }

  function activeCueIndex(cues, time) {
    if (!cues.length || time < cues[0].start) return -1;
    let low = 0;
    let high = cues.length - 1;
    while (low <= high) {
      const middle = Math.floor((low + high) / 2);
      if (cues[middle].start <= time) low = middle + 1;
      else high = middle - 1;
    }
    return Math.max(0, high);
  }

  function routePath(pathname, search, kind, id) {
    return `${pathname}${search}#${kind}=${encodeURIComponent(id)}`;
  }

  function escapeLayer(dialogOpen, lyricsOpen) {
    if (dialogOpen) return 'dialog';
    if (lyricsOpen) return 'lyrics';
    return null;
  }

  function playPresentation(track) {
    return track?.instrumental ? 'sleeve' : 'lyrics';
  }

  function nextLyricMode(mode, event, isPlaying) {
    if (event === 'play') return mode === 'full' ? 'full' : 'peek';
    if (event === 'open') return 'full';
    if (event === 'close') return mode === 'full' && isPlaying ? 'peek' : 'closed';
    return mode;
  }

  function lyricRouteAction(event, { mode = 'closed', ownsEntry = false, hash = '' } = {}) {
    if (event === 'track-change') return mode === 'full' ? 'replace' : null;
    if (event === 'close' && ownsEntry) return 'back';
    if (event === 'close' && /^#track=/.test(hash)) return 'replace';
    return null;
  }

  function lyricCloseLabel(mode) {
    return mode === 'full' ? 'Collapse lyrics' : 'Close lyrics';
  }

  function albumScrollBehavior({ userSelection = false, directLink = false, reducedMotion = false } = {}) {
    if (!userSelection && !directLink) return null;
    return reducedMotion ? 'auto' : 'smooth';
  }

  function initialPlayback({
    recordsPage = false,
    selectedAlbum = null,
    albums = [],
    defaultTrack = null,
    storyQueue = [],
  } = {}, canPlay = () => false) {
    if (recordsPage) {
      const album = albums.find(candidate => candidate.id === selectedAlbum);
      const track = album?.tracks?.find(canPlay);
      if (track) {
        return {
          track,
          queue: buildQueueContext('album', album.id, album.tracks),
        };
      }
    }

    const track = defaultTrack && canPlay(defaultTrack)
      ? defaultTrack
      : storyQueue.find(canPlay);
    return track ? {
      track,
      queue: buildQueueContext('story', 'essay', storyQueue),
    } : null;
  }

  root.ANS_PLAYER_MODEL = {
    buildQueueContext,
    nextPlayable,
    activeCueIndex,
    routePath,
    escapeLayer,
    playPresentation,
    nextLyricMode,
    lyricRouteAction,
    lyricCloseLabel,
    albumScrollBehavior,
    initialPlayback,
  };
})(typeof window === 'undefined' ? globalThis : window);
