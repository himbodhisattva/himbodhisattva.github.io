# Design direction

## Visual system

Keep the current type and colors. Preserve the artwork and editorial scale.
Display type uses Iowan Old Style, Baskerville, Palatino, or Georgia. Interface
text uses Avenir Next, Avenir, Segoe UI, or another local sans serif. The site
does not fetch web fonts.

The main palette uses cold periwinkle `#edf0ff`, plum ink `#272126`, pink
`#bd2167`, dark plum `#211b27`, and pale rose `#f8e4ed`. Album covers supply
the strongest color. Avoid generic beige surfaces and dashboard styling.

## Homepage composition

Open with a large release cover beside the title and lyric. Put a Play control
next to the song. On phones, the cover appears before the copy. Follow with a
short artist note and a sequence of releases. Covers and track lists should
occupy more space than prose.

Use original lyric fragments as display copy. Keep captions and release index
labels short and factual. Do not add a reading-progress line, chapter
navigation, process diagrams, or blocks that explain the meaning of the work.

The longer philosophy essay opens from one understated text link. It remains a
separate reading state with a visible close control and a shareable
`#philosophy` URL.

## Player and lyrics

The site uses a persistent audio element. Playback begins only after a listener acts.
Album playback continues through the chosen track list.

The player stays short and information-dense. Artwork, song metadata, Play,
Next, and Lyrics controls remain large enough to read and tap. Desktop includes
an always-available seek control. Safe-area spacing prevents controls from
colliding with device chrome.

Playing a song opens a compact lyric panel without moving focus. The panel
shows a few lines, centers the active line until the listener scrolls, and can
expand to a full cover-and-lyrics view. A lyric line can seek. Explicit song
selection and Next open lyrics. If the listener closes the panel, automatic
continuation leaves it closed.

Direct song pages show a large Play control over the linked artwork until
playback starts. The copy-link control sits in the lyric header beside Close.
Shared links use the song's title and artwork.

## Records page

Keep the album shelf visible above one selected album detail. Choosing a sleeve
scrolls to that detail and updates the URL. The detail includes the full track
list and a clear album Play control. The homepage and records page use the same
player state and queue rules.

## Interaction and responsive behavior

Every action works with touch and keyboard. Use visible focus indicators,
Escape support, browser Back support, reduced motion, and accurate disabled
states. No action depends on hover. Links use clear language and underlines,
without decorative arrow glyphs.

Review layouts from 320px through 1440px. Homepage releases become one column
on small screens. The records shelf can scroll horizontally while the selected
album remains a full-width detail. Never show a successful playback state when
the audio file is missing.
