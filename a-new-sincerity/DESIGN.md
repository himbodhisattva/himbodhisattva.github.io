# Design direction

## Reading experience
Cold periwinkle reading surface, dark plum ink, large literary display type,
compact practical controls. Use the supplied pink and cyan artwork for the
strongest color. The Friday Girls section uses rose. A darker listening library
makes a distinct destination without becoming a software dashboard. Avoid a
grid of explanatory cards through the story.

Lay out the homepage as short posts interrupted by playable records. Keep the
opening typographic and place the Victory Lap cover after Friday Girls, where it
breaks up the long explanation. Use the source bands only as context. None of their
individual songs should organize the page.

Set the Friday Girls turn as a prominent prose block with a source link. It
should read as part of the essay rather than imitate X's interface.

## Type / color
- Display: locally available Iowan Old Style / Baskerville / Palatino / Georgia.
- Interface/text: locally available Avenir Next / Avenir / Segoe UI / sans-serif.
- No font files are included or fetched. No layout-blocking external font request.
- Cold periwinkle paper `#edf0ff`, ink `#272126`, accent `#bd2167`, dark library `#211b27`, rose
  chapter `#f8e4ed`. More vivid pink remains in record art.

## Interaction
- One persistent audio element. Never autoplay on arrival or scroll. Album
  playback continues through the selected album after the listener starts it.
- Playing a track opens a compact lyric panel above the player without stealing
  focus or blocking the page. It shows only a few lines and keeps the active line
  centered until the listener scrolls. The player can expand it into the full
  inner sleeve, and any lyric line can seek. Explicit track selection and the
  Next control open lyrics; automatic queue continuation leaves them closed if
  the listener dismissed them.
- Keep the player short and dense while giving the artwork, metadata, play
  control, and lyrics label enough size to scan and tap easily. Remove empty
  space before shrinking meaningful controls.
- Keep accordions, cards and routine dialogs out of the story. An
  explicit two-line philosophy link ends the postmodernism coda: the first line
  reads “Now it is our turn to solve postmodernism.” and the second invites the
  reader to open the liner note. It opens a full-page paper-and-ink dialog with
  a visible close control and shareable hash.
- Put the self-awareness argument inside the *(Unfortunately)* album section.
  Break its prose with three large playable track-title rows drawn from that
  record. These rows should look like part of the essay and provide a direct
  listening path.
- Divide the philosophy liner note into three numbered strands. The first
  synthesizes The New Sincerity with metamodernism, then adds performatism and
  fatal strategies as responses to postmodernism. The second treats AI art as a
  medium formed by the speed and recursion of its feedback loop. The third uses
  songwriting and legibility to ask how an act of self-discovery also changes
  the self it describes.
- In-context track links and the standalone records page use the same player
  state and explicit queue context.
- Empty player controls all inherit the selected record on `/records/`; the
  homepage starts at the top of its story queue.
- Artist filters and search preserve titles and versions. Do not invent
  recommendations.
- Share links open a song in the records-page full lyric view without playback.
  The copy-link control sits beside Close in the lyric header.
- Keyboard focus, Escape, arrow keys for tabs, visible focus indicators, reduced
  motion, safe-area spacing. Desktop seeking is always in the mini-player.
- Link affordances come from clear language and underlines. Color and focus
  states reinforce them. Do not append decorative up-right arrow glyphs.
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
chapter rail. The compact lyric panel expands into a full cover-and-words view.
