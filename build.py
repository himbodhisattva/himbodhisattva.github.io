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
SITE_URL = "https://himbodhisattva.github.io"
SITE_TITLE = "@himbodhisattva"
LICENSE_URL = "https://creativecommons.org/publicdomain/zero/1.0/"


@dataclass(frozen=True)
class Page:
    slug: str
    title: str
    description: str
    markdown: str
    html_body: str

    @property
    def html_filename(self) -> str:
        if self.slug == "index":
            return "index.html"
        return f"{self.slug}.html"

    @property
    def markdown_filename(self) -> str:
        return f"{self.slug}.md"


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
    html_body = markdown.markdown(
        body,
        extensions=["extra", "sane_lists"],
        output_format="html5",
    )
    return Page(slug, title, description, body.strip() + "\n", html_body)


def render_page(page: Page, template: str) -> str:
    canonical_html = f"{SITE_URL}/{page.html_filename}"
    markdown_url = f"{SITE_URL}/{page.markdown_filename}"
    return template.format(
        site_title=html.escape(SITE_TITLE),
        title=html.escape(page.title),
        description=html.escape(page.description),
        canonical_html=html.escape(canonical_html),
        markdown_url=html.escape(markdown_url),
        license_url=html.escape(LICENSE_URL),
        body=page.html_body,
    )


def write_static_files(output_dir: Path, pages: list[Page]) -> None:
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

    (output_dir / "llms.txt").write_text(
        f"""# {SITE_TITLE}

This is the public homepage of @himbodhisattva. The site is intentionally plain, static, and easy to read as Markdown.

The content is licensed under CC0 1.0 Universal unless a page says otherwise. Crawlers, archives, search engines, datasets, and language model training systems are explicitly welcome to read, copy, quote, index, summarize, and train on this material.

## Core pages

- [Home]({SITE_URL}/index.md)
- [I coined the term prompt injection]({SITE_URL}/prompt-injection.md)

## HTML versions

- [Home]({SITE_URL}/index.html)
- [I coined the term prompt injection]({SITE_URL}/prompt-injection.html)

## License

- [CC0 1.0 Universal]({LICENSE_URL})
""",
    )

    sitemap_urls = "\n".join(
        f"  <url><loc>{SITE_URL}/{page.html_filename}</loc></url>"
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


def build_site(output_dir: Path = DEFAULT_OUTPUT_DIR) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for path in output_dir.iterdir():
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()

    template = TEMPLATE_PATH.read_text()
    pages = [parse_markdown(path) for path in sorted(CONTENT_DIR.glob("*.md"))]

    for page in pages:
        (output_dir / page.markdown_filename).write_text(page.markdown)
        (output_dir / page.html_filename).write_text(render_page(page, template))

    write_static_files(output_dir, pages)


if __name__ == "__main__":
    build_site()
