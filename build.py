from __future__ import annotations

import html
import shutil
from dataclasses import dataclass
from pathlib import Path

import markdown


ROOT = Path(__file__).parent
CONTENT_DIR = ROOT / "content"
TEMPLATE_PATH = ROOT / "templates" / "page.html"
DEFAULT_OUTPUT_DIR = ROOT / "docs"
SITE_URL = "https://himbodhisattva.com"
SITE_TITLE = "@himbodhisattva"
LICENSE_URL = "https://creativecommons.org/publicdomain/zero/1.0/"
PROOF_DISCLAIMER = (
    "> **Authorship disclaimer:** This proof was written primarily by GPT-5.6-sol."
)
PUBLISHED_FILENAMES = {
    ".nojekyll",
    "CNAME",
    "LICENSE",
    "blog",
    "index.html",
    "index.md",
    "llms.txt",
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
        return f"blog/{self.slug}/"

    @property
    def markdown_url_path(self) -> str:
        if self.is_home:
            return "index.md"
        return f"blog/{self.slug}/index.md"

    @property
    def asset_prefix(self) -> str:
        if self.is_home:
            return ""
        return "../../"


def local_html_path(page: Page) -> str:
    if page.is_home:
        return "index.html"
    return page.html_url_path


def local_markdown_path(page: Page) -> str:
    return page.markdown_url_path


def parse_markdown(path: Path) -> Page:
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


def page_list_markdown(pages: list[Page], section: str | None = None) -> str:
    listed_pages = [
        page
        for page in pages
        if not page.is_home and (section is None or page.section == section)
    ]
    if not listed_pages:
        return "none yet\n"
    return "\n".join(
        f"- [{page.title}]({local_html_path(page)}) ; [markdown]({local_markdown_path(page)})"
        for page in listed_pages
    ) + "\n"


def expand_markdown(body: str, page: Page, pages: list[Page]) -> str:
    if page.is_home:
        return (
            body.replace("{{ pages }}", page_list_markdown(pages).rstrip())
            .replace("{{ proofs }}", page_list_markdown(pages, "proofs").rstrip())
            .replace("{{ posts }}", page_list_markdown(pages, "posts").rstrip())
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


def write_static_files(output_dir: Path, pages: list[Page]) -> None:
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

    sitemap_urls = "\n".join(
        f"  <url><loc>{SITE_URL}/{page.html_url_path}</loc></url>"
        for page in pages
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


def build_site(output_dir: Path = DEFAULT_OUTPUT_DIR, mirror_root: bool = False) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for path in output_dir.iterdir():
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()

    template = TEMPLATE_PATH.read_text()
    pages = [parse_markdown(path) for path in sorted(CONTENT_DIR.glob("*.md"))]

    for page in pages:
        rendered_markdown = expand_markdown(page.markdown, page, pages)
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
    write_static_files(output_dir, pages)

    if mirror_root:
        mirror_to_root(output_dir)


if __name__ == "__main__":
    build_site(mirror_root=True)
