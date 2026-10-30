#!/usr/bin/env python3
"""Build a static folder for /a-new-sincerity/. Does not upload or deploy."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


SOURCE_DIR = Path(__file__).resolve().parent.parent
REPOSITORY_ROOT = SOURCE_DIR.parent
sys.path.insert(0, str(REPOSITORY_ROOT))

import build as site_builder  # noqa: E402


def build(*, publish: bool) -> Path:
    catalog = site_builder.preflight_new_sincerity(SOURCE_DIR)
    output_dir = SOURCE_DIR / "dist" / "a-new-sincerity"
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    for filename in site_builder.NEW_SINCERITY_FILES:
        shutil.copy2(SOURCE_DIR / filename, output_dir / filename)
    for dirname in site_builder.NEW_SINCERITY_DIRS:
        shutil.copytree(SOURCE_DIR / dirname, output_dir / dirname)

    staging_meta = '<meta name="robots" content="noindex,nofollow">'
    if publish:
        for relative_path, canonical_url in site_builder.NEW_SINCERITY_CANONICALS.items():
            page = output_dir / relative_path
            page.write_text(
                page.read_text().replace(
                    staging_meta,
                    f'<link rel="canonical" href="{canonical_url}">',
                )
            )

    site_builder.write_new_sincerity_song_pages(
        SOURCE_DIR,
        output_dir,
        catalog,
        publish=publish,
    )
    urls = (
        tuple(site_builder.NEW_SINCERITY_CANONICALS.values())
        + site_builder.new_sincerity_song_urls(catalog)
    )
    sitemap_urls = "\n".join(f"  <url><loc>{url}</loc></url>" for url in urls)
    (output_dir / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{sitemap_urls}\n"
        "</urlset>\n"
    )
    return output_dir


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--publish",
        action="store_true",
        help="replace noindex with canonical links in the built copy only; does NOT deploy",
    )
    args = parser.parse_args()
    output_dir = build(publish=args.publish)
    if args.publish:
        print(
            "Publication-mode folder prepared. Review audio, credits, privacy and "
            "final covers before uploading."
        )
    else:
        print("Staging folder prepared with noindex retained.")
    print(output_dir)
    print("No files were uploaded or published.")


if __name__ == "__main__":
    main()
