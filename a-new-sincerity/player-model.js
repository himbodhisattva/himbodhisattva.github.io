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

  root.ANS_PLAYER_MODEL = { buildQueueContext, nextPlayable, activeCueIndex, routePath, escapeLayer };
})(typeof window === 'undefined' ? globalThis : window);
