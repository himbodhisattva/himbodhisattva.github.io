# Design direction

## Reading experience
Quiet warm-paper reading surface, dark plum ink, large literary display type,
compact practical controls. Use the supplied pink and cyan artwork for the
strongest color. The Friday Girls section uses rose. A darker listening library
makes a distinct destination without becoming a software dashboard. Avoid a
grid of explanatory cards through the story.

Lay out the homepage as short posts interrupted by playable records. Give the
Victory Lap title and review excerpt the most space. Use the source bands only
as context. None of their individual songs should organize the page.

## Type / color
- Display: locally available Iowan Old Style / Baskerville / Palatino / Georgia.
- Interface/text: locally available Avenir Next / Avenir / Segoe UI / sans-serif.
- No font files are included or fetched. No layout-blocking external font request.
- Paper `#f5f2eb`, ink `#272126`, accent `#bd2167`, dark library `#211b27`, rose
  chapter `#f8e4ed`. More vivid pink remains in record art.

## Interaction
- One persistent audio element. Never autoplay on arrival or scroll. Album
  playback continues through the selected album after the listener starts it.
- Timed lyrics open as a full inner-sleeve theater above the player. The active
  line stays centered until the listener scrolls; any lyric line can seek.
- Put the deeper prose in a single pull-out liner-note deck. Keep accordions,
  cards and dialogs out of the story.
- Show the steps from album to review to sampled song in one horizontal strip.
- In-context track links and the standalone records page use the same player
  state and explicit queue context.
- Artist filters and search preserve titles and versions. Do not invent
  recommendations.
- Share links open a song in the records-page lyric theater without playback.
- Keyboard focus, Escape, arrow keys for tabs, visible focus indicators, reduced
  motion, safe-area spacing. Desktop seeking is always in the mini-player.
- Never simulate successful playback when a recording is absent.

## Future motion / video
Use motion only when the interface changes state. Keep the reading surface still.
A future video should be optional and user-triggered. Use an optimized poster,
no audio autoplay, and `preload="none"`. Preserve a completely usable text/audio
experience without the video. Prefer explicit texture footage over fake archival
footage of the actual college band.

## Responsive
Reviewed from 320px through 1440px. The essay becomes one column at phone sizes. The records
page uses a horizontal sleeve shelf and one full album stage. Desktop keeps a
chapter rail and gives the lyric theater room for the cover beside the words.
