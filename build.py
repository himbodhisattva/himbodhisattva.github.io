from __future__ import annotations

import html
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).parent
CONTENT_DIR = ROOT / "content"
TEMPLATE_PATH = ROOT / "templates" / "page.html"
DEFAULT_OUTPUT_DIR = ROOT / "docs"
SITE_URL = "https://himbodhisattva.com"
SITE_TITLE = "@himbodhisattva"
NEW_SINCERITY_SOURCE_DIR = ROOT / "a-new-sincerity"
NEW_SINCERITY_FILES = (
    "index.html",
    "style.css",
    "experience.css",
    "hybrid-preview.css",
    "app.js",
    "player-model.js",
    "data.js",
    "lyrics-sync.js",
    "favicon.ico",
)
NEW_SINCERITY_DIRS = ("assets", "audio", "records")
NEW_SINCERITY_CANONICALS = {
    "index.html": f"{SITE_URL}/a-new-sincerity/",
    "records/index.html": f"{SITE_URL}/a-new-sincerity/records/",
}
NEW_SINCERITY_BASE_URL = f"{SITE_URL}/a-new-sincerity"
NEW_SINCERITY_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
NEW_SINCERITY_METADATA_MARKER = "<!-- ans-song-metadata -->"
LICENSE_URL = "https://creativecommons.org/publicdomain/zero/1.0/"
PROOF_DISCLAIMER = (
    "> **Authorship disclaimer:** This proof was written primarily by GPT-5.6-sol."
)
PROJECTS_MARKDOWN = "## projects\n\n- [a new sincerity](a-new-sincerity/)"
PUBLISHED_FILENAMES = {
    ".nojekyll",
    "CNAME",
    "LICENSE",
    "blog",
    "index.html",
    "index.md",
    "llms.txt",
    "proofs",
    "robots.txt",
    "sitemap.xml",
    "style.css",
}
STALE_ROOT_FILENAMES = {
    "prompt-injection.html",
    "prompt-injection.md",
}


@dataclass(frozen=True)
class Page:
    slug: str
    title: str
    description: str
    section: str
    markdown: str
    html_body: str

    @property
    def is_home(self) -> bool:
        if self.slug == "index":
            return True
        return False

    @property
    def output_dir(self) -> Path:
        if self.is_home:
            return Path(".")
        if self.section == "indexes":
            return Path(self.slug)
        return Path("blog") / self.slug

    @property
    def html_output_path(self) -> Path:
        return self.output_dir / "index.html"

    @property
    def markdown_output_path(self) -> Path:
        return self.output_dir / "index.md"

    @property
    def html_url_path(self) -> str:
        if self.is_home:
            return ""
        return f"{self.output_dir.as_posix()}/"

    @property
    def markdown_url_path(self) -> str:
        if self.is_home:
            return "index.md"
        return f"{self.output_dir.as_posix()}/index.md"

    @property
    def asset_prefix(self) -> str:
        if self.is_home:
            return ""
        return "../" * len(self.output_dir.parts)


def local_html_path(page: Page) -> str:
    if page.is_home:
        return "index.html"
    return page.html_url_path


def local_markdown_path(page: Page) -> str:
    return page.markdown_url_path


def parse_markdown(path: Path) -> Page:
    import markdown

    raw = path.read_text()
    metadata: dict[str, str] = {}
    body = raw

    if raw.startswith("---\n"):
        _, header, body = raw.split("---\n", 2)
        for line in header.splitlines():
            if not line.strip():
                continue
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip().strip('"')

    slug = path.stem
    title = metadata.get("title", slug.replace("-", " ").title())
    description = metadata.get("description", title)
    section = metadata.get("section", "posts")
    html_body = markdown.markdown(
        body,
        extensions=["extra", "sane_lists"],
        output_format="html5",
    )
    return Page(slug, title, description, section, body.strip() + "\n", html_body)


def page_list_markdown(
    pages: list[Page], section: str | None = None, link_prefix: str = ""
) -> str:
    listed_pages = [
        page
        for page in pages
        if not page.is_home and (section is None or page.section == section)
    ]
    if not listed_pages:
        return "none yet\n"
    return "\n".join(
        f"- [{page.title}]({link_prefix}{local_html_path(page)}) ; "
        f"[markdown]({link_prefix}{local_markdown_path(page)})"
        for page in listed_pages
    ) + "\n"


def expand_markdown(
    body: str,
    page: Page,
    pages: list[Page],
    include_new_sincerity: bool = False,
) -> str:
    body = (
        body.replace(
            "{{ pages }}",
            page_list_markdown(pages, link_prefix=page.asset_prefix).rstrip(),
        )
        .replace(
            "{{ proofs }}",
            page_list_markdown(
                pages, "proofs", link_prefix=page.asset_prefix
            ).rstrip(),
        )
        .replace(
            "{{ posts }}",
            page_list_markdown(
                pages, "posts", link_prefix=page.asset_prefix
            ).rstrip(),
        )
        .replace(
            "{{ projects }}",
            PROJECTS_MARKDOWN if include_new_sincerity else "",
        )
    )
    if page.section == "proofs":
        heading, separator, remainder = body.partition("\n")
        if separator and heading.startswith("# "):
            remainder = remainder.lstrip("\n")
            return f"{heading}\n\n{PROOF_DISCLAIMER}\n\n{remainder}"
        return f"{PROOF_DISCLAIMER}\n\n{body}"
    return body


def render_page(page: Page, template: str) -> str:
    canonical_html = f"{SITE_URL}/{page.html_url_path}"
    markdown_url = f"{SITE_URL}/{page.markdown_url_path}"
    return template.format(
        site_title=html.escape(SITE_TITLE),
        title=html.escape(page.title),
        description=html.escape(page.description),
        canonical_html=html.escape(canonical_html),
        markdown_url=html.escape(markdown_url),
        license_url=html.escape(LICENSE_URL),
        home_url=html.escape(f"{page.asset_prefix}index.html"),
        style_url=html.escape(f"{page.asset_prefix}style.css"),
        llms_url=html.escape(f"{page.asset_prefix}llms.txt"),
        local_license_url=html.escape(f"{page.asset_prefix}LICENSE"),
        body=page.html_body,
    )


def write_static_files(
    output_dir: Path,
    pages: list[Page],
    include_new_sincerity: bool = False,
    new_sincerity_release_urls: tuple[str, ...] = (),
) -> None:
    (output_dir / "CNAME").write_text("himbodhisattva.com\n")

    (output_dir / "style.css").write_text(
        """html {
  color-scheme: light;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 17px;
  line-height: 1.55;
}

body {
  background: #fff;
  color: #000;
  margin: 0;
}

header,
main,
footer {
  max-width: 74ch;
  padding: 1rem;
}

header {
  border-bottom: 1px solid #000;
}

footer {
  border-top: 1px solid #000;
  font-size: 0.9rem;
}

a {
  color: #000;
  overflow-wrap: anywhere;
  text-decoration: underline;
}

h1,
h2,
h3 {
  font-size: 1rem;
  line-height: 1.25;
  margin: 1.5rem 0 0.5rem;
}

h1 {
  font-size: 1.25rem;
}

blockquote {
  border-left: 3px solid #000;
  margin-left: 0;
  padding-left: 1rem;
}

table {
  border-collapse: collapse;
  display: block;
  max-width: 100%;
  overflow-x: auto;
}

th,
td {
  border: 1px solid #000;
  padding: 0.35rem 0.5rem;
  vertical-align: top;
}

code {
  font-family: inherit;
}

@media (max-width: 640px) {
  html {
    font-size: 16px;
  }

  header,
  main,
  footer {
    padding: 0.85rem;
  }
}
""",
    )

    (output_dir / "robots.txt").write_text(
        f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
""",
    )

    ordered_pages = [page for page in pages if page.is_home] + [
        page for page in pages if not page.is_home
    ]
    core_pages = "\n".join(
        f"- [{'Home' if page.is_home else page.title}]({SITE_URL}/{page.markdown_url_path})"
        for page in ordered_pages
    )
    html_versions = "\n".join(
        f"- [{'Home' if page.is_home else page.title}]({SITE_URL}/{page.html_url_path})"
        for page in ordered_pages
    )
    (output_dir / "llms.txt").write_text(
        f"""# {SITE_TITLE}

This is the public homepage of @himbodhisattva. The site is intentionally plain, static, and easy to read as Markdown.

The content is licensed under CC0 1.0 Universal unless a page says otherwise. Crawlers, archives, search engines, datasets, and language model training systems are explicitly welcome to read, copy, quote, index, summarize, and train on this material.

## Core pages

{core_pages}

## HTML versions

{html_versions}

## License

- [CC0 1.0 Universal]({LICENSE_URL})
""",
    )

    sitemap_entries = [
        f"{SITE_URL}/{page.html_url_path}" for page in ordered_pages
    ]
    if include_new_sincerity:
        sitemap_entries[1:1] = NEW_SINCERITY_CANONICALS.values()
        sitemap_entries[3:3] = new_sincerity_release_urls
    sitemap_entries = list(dict.fromkeys(sitemap_entries))
    sitemap_urls = "\n".join(
        f"  <url><loc>{url}</loc></url>" for url in sitemap_entries
    )
    (output_dir / "sitemap.xml").write_text(
        f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{sitemap_urls}
</urlset>
""",
    )

    (output_dir / "LICENSE").write_text(
        f"""CC0 1.0 Universal Public Domain Dedication

Unless otherwise noted, the original text published on this site by @himbodhisattva is dedicated to the public domain under CC0 1.0 Universal.

You may copy, modify, distribute, index, quote, summarize, embed, archive, and train machine learning systems on this material without asking permission.

License deed: {LICENSE_URL}
Legal code: https://creativecommons.org/publicdomain/zero/1.0/legalcode.en
""",
    )


def mirror_to_root(output_dir: Path) -> None:
    for filename in PUBLISHED_FILENAMES | STALE_ROOT_FILENAMES:
        target = ROOT / filename
        if target.is_dir():
            shutil.rmtree(target)
        elif target.exists():
            target.unlink()

    for filename in PUBLISHED_FILENAMES:
        source = output_dir / filename
        target = ROOT / filename
        if source.is_dir():
            shutil.copytree(source, target)
        else:
            shutil.copyfile(source, target)


def _new_sincerity_asset(source_dir: Path, value: object, owner: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{owner} has no artwork")
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts or relative.parts[:1] != ("assets",):
        raise ValueError(f"{owner} has unsafe artwork path: {value!r}")
    candidate = source_dir / relative
    if not candidate.is_file():
        raise FileNotFoundError(f"{owner} artwork does not exist: {candidate}")
    return value


def load_new_sincerity_catalog(source_dir: Path) -> dict[str, object]:
    data_path = source_dir / "data.js"
    source = data_path.read_text()
    match = re.fullmatch(
        r"\s*window\.ANS_DATA\s*=\s*(\{.*\})\s*;\s*",
        source,
        flags=re.DOTALL,
    )
    if match is None:
        raise ValueError(f"could not parse A New Sincerity catalog: {data_path}")
    catalog = json.loads(match.group(1))
    albums = catalog.get("albums")
    tracks = catalog.get("tracks")
    if not isinstance(albums, list) or not isinstance(tracks, list):
        raise ValueError("A New Sincerity catalog needs album and track lists")

    album_by_id: dict[str, dict[str, object]] = {}
    for album in albums:
        if not isinstance(album, dict):
            raise ValueError("A New Sincerity album entries must be objects")
        album_id = album.get("id")
        if not isinstance(album_id, str) or NEW_SINCERITY_ID.fullmatch(album_id) is None:
            raise ValueError(f"unsafe A New Sincerity album ID: {album_id!r}")
        if album_id in album_by_id:
            raise ValueError(f"duplicate A New Sincerity album ID: {album_id}")
        if not isinstance(album.get("title"), str) or not album["title"]:
            raise ValueError(f"album {album_id} has no title")
        if not isinstance(album.get("artist"), str) or not album["artist"]:
            raise ValueError(f"album {album_id} has no artist")
        _new_sincerity_asset(source_dir, album.get("art"), f"album {album_id}")
        album_by_id[album_id] = album

    track_by_id: dict[str, dict[str, object]] = {}
    for track in tracks:
        if not isinstance(track, dict):
            raise ValueError("A New Sincerity track entries must be objects")
        track_id = track.get("id")
        if not isinstance(track_id, str) or NEW_SINCERITY_ID.fullmatch(track_id) is None:
            raise ValueError(f"unsafe A New Sincerity track ID: {track_id!r}")
        if track_id in track_by_id:
            raise ValueError(f"duplicate A New Sincerity track ID: {track_id}")
        album_id = track.get("album")
        if album_id not in album_by_id:
            raise ValueError(f"track {track_id} references unknown album: {album_id!r}")
        if not isinstance(track.get("title"), str) or not track["title"]:
            raise ValueError(f"track {track_id} has no title")
        artist = track.get("artist", album_by_id[album_id]["artist"])
        if not isinstance(artist, str) or not artist:
            raise ValueError(f"track {track_id} has no artist")
        if track.get("art") is not None:
            _new_sincerity_asset(source_dir, track["art"], f"track {track_id}")
        track_by_id[track_id] = track

    route_collisions = set(album_by_id) & set(track_by_id)
    if route_collisions:
        collision = sorted(route_collisions)[0]
        raise ValueError(f"route ID is both an album and a track: {collision}")

    listed_tracks: set[str] = set()
    for album_id, album in album_by_id.items():
        album_tracks = album.get("tracks")
        if not isinstance(album_tracks, list):
            raise ValueError(f"album {album_id} has no track list")
        for track_id in album_tracks:
            if track_id not in track_by_id:
                raise ValueError(f"album {album_id} references unknown track: {track_id!r}")
            if track_id in listed_tracks:
                raise ValueError(f"track {track_id} appears in more than one album track list")
            if track_by_id[track_id]["album"] != album_id:
                raise ValueError(f"track {track_id} is listed under the wrong album")
            listed_tracks.add(track_id)
    unlisted = set(track_by_id) - listed_tracks
    if unlisted:
        raise ValueError(f"tracks missing from album track lists: {', '.join(sorted(unlisted))}")

    return catalog


def new_sincerity_song_urls(catalog: dict[str, object]) -> tuple[str, ...]:
    return tuple(
        f"{NEW_SINCERITY_BASE_URL}/records/{quote(track['id'], safe='')}/"
        for track in catalog["tracks"]
    )


def new_sincerity_album_urls(catalog: dict[str, object]) -> tuple[str, ...]:
    return tuple(
        f"{NEW_SINCERITY_BASE_URL}/records/{quote(album['id'], safe='')}/"
        for album in catalog["albums"]
    )


def new_sincerity_record_urls(catalog: dict[str, object]) -> tuple[str, ...]:
    return new_sincerity_album_urls(catalog) + new_sincerity_song_urls(catalog)


def _remove_share_metadata(page: str) -> str:
    def remove_meta(match: re.Match[str]) -> str:
        tag = match.group(0)
        key = re.search(r"\b(?:name|property)=[\"']([^\"']+)[\"']", tag, re.I)
        if key and (
            key.group(1).lower() in {"description", "robots"}
            or key.group(1).lower().startswith("og:")
            or key.group(1).lower().startswith("twitter:")
        ):
            return ""
        return tag

    page = re.sub(r"<meta\b[^>]*>", remove_meta, page, flags=re.I)
    page = re.sub(
        r"<link\b(?=[^>]*\brel=[\"']canonical[\"'])[^>]*>",
        "",
        page,
        flags=re.I,
    )
    page, base_count = re.subn(
        r"<base\b[^>]*>",
        NEW_SINCERITY_METADATA_MARKER,
        page,
        flags=re.I,
    )
    if base_count != 1:
        raise ValueError("A New Sincerity records page needs exactly one base tag")
    return re.sub(r"<title\b[^>]*>.*?</title>", "", page, flags=re.I | re.S)


def _render_new_sincerity_share_page(
    records_shell: str,
    *,
    record_id: str,
    title: str,
    artist: str,
    description: str,
    art: str,
    image_alt: str,
    open_graph_type: str,
    publish: bool,
) -> str:
    record_url = f"{NEW_SINCERITY_BASE_URL}/records/{quote(record_id, safe='')}/"
    art_url = f"{NEW_SINCERITY_BASE_URL}/{quote(art, safe='/')}"
    visibility = (
        f'<link rel="canonical" href="{html.escape(record_url, quote=True)}">'
        if publish
        else '<meta name="robots" content="noindex,nofollow">'
    )
    metadata = f"""
<meta name="description" content="{html.escape(description, quote=True)}">
{visibility}
<meta property="og:title" content="{html.escape(title, quote=True)}">
<meta property="og:description" content="{html.escape(description, quote=True)}">
<meta property="og:type" content="{html.escape(open_graph_type, quote=True)}">
<meta property="og:url" content="{html.escape(record_url, quote=True)}">
<meta property="og:image" content="{html.escape(art_url, quote=True)}">
<meta property="og:image:alt" content="{html.escape(image_alt, quote=True)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html.escape(title, quote=True)}">
<meta name="twitter:description" content="{html.escape(description, quote=True)}">
<meta name="twitter:image" content="{html.escape(art_url, quote=True)}">
<meta name="twitter:image:alt" content="{html.escape(image_alt, quote=True)}">
<base href="../../">
<title>{html.escape(title)} · {html.escape(artist)}</title>
""".strip()
    page = _remove_share_metadata(records_shell)
    page = page.replace(NEW_SINCERITY_METADATA_MARKER, metadata, 1)
    head, separator, body = page.partition("</head>")
    if not separator:
        raise ValueError("A New Sincerity records page has no closing head tag")
    head = re.sub(r"\n{3,}", "\n\n", head)
    return f"{head}{separator}{body}"


def render_new_sincerity_song_page(
    records_shell: str,
    track: dict[str, object],
    album: dict[str, object],
    *,
    publish: bool,
) -> str:
    title = track["title"]
    artist = track.get("artist", album["artist"])
    return _render_new_sincerity_share_page(
        records_shell,
        record_id=track["id"],
        title=title,
        artist=artist,
        description=f"{artist} · {album['title']}",
        art=track.get("art") or album["art"],
        image_alt=f"{title} artwork",
        open_graph_type="music.song",
        publish=publish,
    )


def render_new_sincerity_album_page(
    records_shell: str,
    album: dict[str, object],
    *,
    publish: bool,
) -> str:
    track_count = len(album["tracks"])
    track_label = "track" if track_count == 1 else "tracks"
    title = album["title"]
    artist = album["artist"]
    return _render_new_sincerity_share_page(
        records_shell,
        record_id=album["id"],
        title=title,
        artist=artist,
        description=f"{artist} · {track_count} {track_label}",
        art=album["art"],
        image_alt=f"{title} album artwork",
        open_graph_type="music.album",
        publish=publish,
    )


def write_new_sincerity_song_pages(
    source_dir: Path,
    target_dir: Path,
    catalog: dict[str, object],
    *,
    publish: bool,
) -> None:
    shell = (source_dir / "records" / "index.html").read_text()
    albums = {album["id"]: album for album in catalog["albums"]}
    for track in catalog["tracks"]:
        destination = target_dir / "records" / track["id"] / "index.html"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            render_new_sincerity_song_page(
                shell,
                track,
                albums[track["album"]],
                publish=publish,
            )
        )


def write_new_sincerity_album_pages(
    source_dir: Path,
    target_dir: Path,
    catalog: dict[str, object],
    *,
    publish: bool,
) -> None:
    shell = (source_dir / "records" / "index.html").read_text()
    for album in catalog["albums"]:
        destination = target_dir / "records" / album["id"] / "index.html"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            render_new_sincerity_album_page(
                shell,
                album,
                publish=publish,
            )
        )


def preflight_new_sincerity(source_dir: Path) -> dict[str, object]:
    """Validate every input needed to publish the listening site."""
    manifest_path = source_dir / "media-manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"missing A New Sincerity manifest: {manifest_path}")
    manifest = json.loads(manifest_path.read_text())
    referenced_audio = {
        track["audio"] for track in manifest["tracks"].values() if track.get("audio")
    }
    missing_audio = sorted(
        audio_path
        for audio_path in referenced_audio
        if not (source_dir / audio_path).is_file()
    )
    if not referenced_audio or missing_audio:
        missing = ", ".join(missing_audio) or "manifest has no audio paths"
        raise FileNotFoundError(f"A New Sincerity publication is incomplete: {missing}")

    for filename in NEW_SINCERITY_FILES:
        source = source_dir / filename
        if not source.is_file():
            raise FileNotFoundError(f"missing A New Sincerity file: {source}")

    for dirname in NEW_SINCERITY_DIRS:
        source = source_dir / dirname
        if not source.is_dir():
            raise FileNotFoundError(f"missing A New Sincerity directory: {source}")

    staging_meta = '<meta name="robots" content="noindex,nofollow">'
    for relative_path in NEW_SINCERITY_CANONICALS:
        page = source_dir / relative_path
        if page.read_text().count(staging_meta) != 1:
            raise ValueError(f"expected one staging robots tag in {page}")

    catalog = load_new_sincerity_catalog(source_dir)
    manifest_tracks = manifest.get("tracks")
    if not isinstance(manifest_tracks, dict):
        raise ValueError("A New Sincerity manifest needs a track map")
    for track in catalog["tracks"]:
        track_id = track["id"]
        audio_path = track.get("audio")
        if not isinstance(audio_path, str) or not audio_path:
            raise ValueError(f"track {track_id} has no audio path")
        relative_audio = Path(audio_path)
        if (
            relative_audio.is_absolute()
            or ".." in relative_audio.parts
            or relative_audio.parts[:1] != ("audio",)
        ):
            raise ValueError(f"track {track_id} has unsafe audio path: {audio_path!r}")
        if not (source_dir / relative_audio).is_file():
            raise FileNotFoundError(
                f"track {track_id} audio does not exist: {source_dir / relative_audio}"
            )
        manifest_track = manifest_tracks.get(track_id)
        if not isinstance(manifest_track, dict) or manifest_track.get("audio") != audio_path:
            raise ValueError(
                f"track {track_id} audio does not match the media manifest: "
                f"{audio_path!r}"
            )
    records_shell = (source_dir / "records" / "index.html").read_text()
    albums = {album["id"]: album for album in catalog["albums"]}
    for album in catalog["albums"]:
        render_new_sincerity_album_page(
            records_shell,
            album,
            publish=True,
        )
    for track in catalog["tracks"]:
        render_new_sincerity_song_page(
            records_shell,
            track,
            albums[track["album"]],
            publish=True,
        )
    return catalog


def publish_new_sincerity(
    source_dir: Path,
    output_dir: Path,
    catalog: dict[str, object] | None = None,
) -> None:
    """Copy the reviewed listening site into the GitHub Pages output tree."""
    catalog = catalog or preflight_new_sincerity(source_dir)

    target_dir = output_dir / "a-new-sincerity"
    if target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.mkdir(parents=True)

    for filename in NEW_SINCERITY_FILES:
        source = source_dir / filename
        shutil.copy2(source, target_dir / filename)

    for dirname in NEW_SINCERITY_DIRS:
        source = source_dir / dirname
        shutil.copytree(source, target_dir / dirname)

    staging_meta = '<meta name="robots" content="noindex,nofollow">'
    for relative_path, canonical_url in NEW_SINCERITY_CANONICALS.items():
        page = target_dir / relative_path
        html_text = page.read_text()
        canonical = f'<link rel="canonical" href="{canonical_url}">'
        page.write_text(html_text.replace(staging_meta, canonical))

    write_new_sincerity_song_pages(
        source_dir,
        target_dir,
        catalog,
        publish=True,
    )
    write_new_sincerity_album_pages(
        source_dir,
        target_dir,
        catalog,
        publish=True,
    )


def build_site(
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    mirror_root: bool = False,
    new_sincerity_source: Path | None = None,
) -> None:
    import markdown

    new_sincerity_catalog = None
    if new_sincerity_source is not None:
        new_sincerity_catalog = preflight_new_sincerity(new_sincerity_source)

    output_dir.mkdir(parents=True, exist_ok=True)
    for path in output_dir.iterdir():
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()

    template = TEMPLATE_PATH.read_text()
    pages = [parse_markdown(path) for path in sorted(CONTENT_DIR.glob("*.md"))]

    for page in pages:
        rendered_markdown = expand_markdown(
            page.markdown,
            page,
            pages,
            include_new_sincerity=new_sincerity_source is not None,
        )
        rendered_page = Page(
            slug=page.slug,
            title=page.title,
            description=page.description,
            section=page.section,
            markdown=rendered_markdown,
            html_body=markdown.markdown(
                rendered_markdown,
                extensions=["extra", "sane_lists"],
                output_format="html5",
            ),
        )
        page_dir = output_dir / page.output_dir
        page_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / page.markdown_output_path).write_text(rendered_page.markdown)
        (output_dir / page.html_output_path).write_text(render_page(rendered_page, template))

    (output_dir / ".nojekyll").write_text("")
    write_static_files(
        output_dir,
        pages,
        include_new_sincerity=new_sincerity_source is not None,
        new_sincerity_release_urls=(
            new_sincerity_record_urls(new_sincerity_catalog)
            if new_sincerity_catalog is not None
            else ()
        ),
    )

    if new_sincerity_source is not None:
        publish_new_sincerity(
            new_sincerity_source,
            output_dir,
            catalog=new_sincerity_catalog,
        )

    if mirror_root:
        mirror_to_root(output_dir)


if __name__ == "__main__":
    build_site(
        mirror_root=True,
        new_sincerity_source=NEW_SINCERITY_SOURCE_DIR,
    )
