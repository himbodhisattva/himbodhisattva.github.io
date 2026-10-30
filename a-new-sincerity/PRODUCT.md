# Product contract

## Purpose

A New Sincerity is an artist site and playable release catalog. The homepage
opens on the first release and presents the records chronologically. The
writing stays attached to those releases instead of becoming a separate
explanation.

## Homepage

- Keep the existing typography, palette, album artwork, and visual direction.
- Give album art and music most of the page. Show release covers, useful play
  controls, and compact track lists.
- Keep visible homepage prose between roughly 450 and 650 words. Each bit of
  context follows its release cover and Play control, so the story accumulates
  without becoming a freestanding explainer.
- Keep the release sequence chronological: *(Unfortunately)*, *Revisionist
  History*, Friday Girls, *Somehow Both a Victory Lap and a Cry for Help*, then
  *My Art Machine*.
- Use the line “my art machine has the right aesthetics / that's how you know
  i'm so authentic.” Do not add a thesis about what the work proves or how a
  listener should receive it.
- Preserve the unresolved questions about authorship, artificial performers,
  audience feedback, and what counts as real.
- Include one small link to the longer philosophy essay. The full essay remains
  available only when a visitor chooses to open it.
- Exclude reading progress, a chapter rail, explanatory diagrams, full theory
  modules, favorite badges, and listening instructions.
- Credit production in the footer as “all songs made with Suno v6-pro,” with
  “Suno v6-pro” linked to `https://suno.com/`.

The public identity is A New Sincerity. Do not add private family details,
clinical labels, employer information, or material from private transcripts.

## Records

`/records/` is a standalone, scannable catalog. Its album shelf stays above the
selected release. Selecting an album uses its static `/records/<album-id>/`
URL, scrolls to its full track list, and creates an album queue. Each album URL
shows the release title and artist beside its cover in link previews.
Reduced-motion settings replace smooth scrolling with an immediate jump.

Album artwork links to the corresponding release. Song titles and version
labels remain exact. The catalog does not invent recommendations or rankings.

## Playback and song links

The homepage and records page share one catalog and one persistent player.
Starting an album plays its tracks in order. Before a listener chooses a song,
every player control uses the same default: the selected record on `/records/`,
or the first playable homepage track.

Playing or explicitly selecting a song opens a compact lyric view. The active
lines follow playback and scroll into view. A listener can expand the full
lyrics, seek from a lyric line, or close the panel. Automatic queue changes do
not reopen lyrics after the listener closes them.

Each song has a static `/records/<track-id>/` page with its own title, artwork,
and share metadata. A direct song link opens the song paused with its lyrics or
sleeve visible and a large Play control over the artwork. Player controls remain
compact, readable, keyboard accessible, and comfortable to tap. Playback never
starts on page load.

## Delivery

The site is static and supports a portable local preview. Local audio and timed
lyric cues power the player; songs without cue data fall back to untimed lines.
The site does not load X's widget script.
