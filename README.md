# @himbodhisattva homepage

Plain static homepage for `@himbodhisattva`, optimized for direct reading by
humans, crawlers, archives, and language models.

## Build

```sh
uv run python build.py
```

The generated GitHub Pages site lives in `docs/`.

## Test

```sh
uv run pytest
```

## Publish

```sh
scripts/publish.sh
```

Use a custom commit message with:

```sh
scripts/publish.sh "Update posts"
```
