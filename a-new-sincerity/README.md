# A New Sincerity

This static site combines a multimedia essay with a separate catalog at
`/a-new-sincerity/records/`. Both pages use the same audio player, album queues,
artwork, track data and timed lyrics. The working copy retains
`noindex,nofollow`; the parent site's build creates the canonical public copy.

## Local media

The catalog contains six albums and 48 entries. Each entry has a 256 kbps MP3
with metadata for its album context. Every album has a cover. The source masters remain in `~/Music/Suno Albums`.
`LOCAL-ASSETS.json` records the local mapping and stays outside Git.

## Pages

- `index.html` contains the essay, featured tracks and one shared liner-note
  deck for optional context.
- `records/index.html` contains the direct-linkable album catalog. Selecting an
  album updates one album stage instead of opening a modal.
- `story.md` keeps the site prose in an editable form.

The site identifies itself as A New Sincerity. The parent site's persona does
not appear as the section's brand or byline.

## Player and lyrics

`app.js` owns one `HTMLAudioElement`. Each play action supplies an explicit
queue context. An album row, album button or album-linked story feature keeps
the album order even after the listener opens lyrics. Natural completion stops
after the final album track; manual previous and next controls may wrap.

Playing a track opens a compact lyric panel above the persistent player.
`lyrics-sync.js` maps each supplied lyric line to the matching local recording,
keeps the active line in view and lets a listener click any line to seek. The
player can expand the panel into a full inner sleeve. Manual scrolling pauses
automatic following until the listener presses “follow the song.” Tracks
without generated cues use a duration-weighted fallback. Instrumentals display
their sleeve without invented lyrics.

To regenerate cues from the current MP3 files:

```sh
uv run --no-project tools/generate_lyric_sync.py
```

The generator runs word-timestamped MLX Whisper locally, aligns recognized words
to the supplied lyric sequence, and writes line cues. It does not replace or
rewrite lyrics.

## Run and verify

Serve the source directory from an HTTP origin:

```sh
npm start
```

Then open `http://localhost:8000/` and `http://localhost:8000/records/`.

Run the source, catalog, queue and syntax checks with:

```sh
npm test
```

Build the staging folder with:

```sh
npm run build
```

The build appears in `dist/a-new-sincerity/` with staging metadata intact. The
`--publish` option replaces `noindex` with canonical links in the built copy,
but does not upload or deploy anything.

## Publication

Run `scripts/publish.sh` from the parent repository. Its builder copies this
site and its audio into `docs/a-new-sincerity/`, replaces the staging robots
tags with canonical links, and adds both public routes to the sitemap. The
source pages keep their staging metadata so local drafts are never mistaken for
the public build.
