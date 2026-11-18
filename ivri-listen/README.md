# Ivri listening review

The unlisted public page at https://himbodhisattva.com/ivri-listen/ has two sets of three comparisons (`?set=1` and `?set=2`). Each session assigns A/B randomly per pair and keeps the order in browser storage. The page asks separately about target-word stress and whole-reading naturalness. It offers both, neither, unsure, skip and an optional note.

Audio bytes come unchanged from the frozen six-pair experiment. `pairs.json` records their SHA-256 values; `provenance.json` identifies the models and runtimes. Target indices distinguish repeated words and prefixed forms. Answers are experimental feedback, not teaching approval.

The collector is a separate Sites project, `appgprj_6afc6a76acfc8191a19a6c955ba4d0a4`. Its source is maintained in the Ivri repository under `tools/audio/listening-review-collector`. The frontend sends to `/api/reviews` at https://ivri-listening-review.samh.chatgpt.site. There is no public response-reading endpoint. Retrieve answers through authenticated Sites database tools. Exclude synthetic workflow checks identified by their QA alias and note.

`build.py` copies this directory to `docs/ivri-listen/`; Pages serves `main:/docs`. The page is excluded from the homepage and sitemap and requests no indexing. The URL is public, not access-controlled. No emails or microphone recordings are collected. Optional aliases and comments are private responses, so never commit collected answers here.

For local QA, serve the parent directory on LAN port 4311 and run the collector preview on LAN port 4312. The frontend uses that collector only on the named LAN hostname. It preserves pending submissions and retries identical bytes after an ambiguous failure. A confirmed duplicate preserves the first submitted answer and allows continuation.

## Opening sound review

The `sounds/` directory prepares three sets of four single-sound judgments at
`sounds/?set=1`, `sounds/?set=2` and `sounds/?set=3`. These pages are not published.
The twelve unchanged teacher WAVs use their full SHA-256 in their filenames.
The matching collector route is `/api/sound-reviews`; its frozen manifest binds
each answer to the audio, synthesis request and authored course target.

Run `node --test tests/sound-review.test.mjs` from the repository root. The seven
tests cover the audio identities, set coverage, pending-response preservation,
retry, conflict and rejection behavior. Local browser checks cover the first
sound, a labeled synthetic save to SQLite and resume at the second sound after
reload. The phone layout fits at 390 by 844 CSS pixels. The test tab is closed.

Browser checks for interrupted saves, conflicting responses, skipped items,
all three sets and desktop layout remain open. Independent product critique,
the static site build and deployment also remain open. Preserve old stress
reviews when completing this work. Keep synthetic checks separate from fluent
judgments; feedback does not create a teaching approval receipt.
