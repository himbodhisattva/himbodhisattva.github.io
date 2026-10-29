# @himbodhisattva homepage

Plain static homepage for `@himbodhisattva`, optimized for people and automated
readers.

## Build

```sh
uv run python build.py
```

The generated GitHub Pages site lives in `docs/`.
The build also publishes the reviewed A New Sincerity source at
`docs/a-new-sincerity/`, including its local audio library.

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
