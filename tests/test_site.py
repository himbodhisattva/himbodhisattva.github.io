import json
from xml.etree import ElementTree

import pytest


def _new_sincerity_fixture(tmp_path):
    source_dir = tmp_path / "a-new-sincerity"
    (source_dir / "assets").mkdir(parents=True)
    (source_dir / "audio").mkdir()
    (source_dir / "records").mkdir()

    staging_meta = '<meta name="robots" content="noindex,nofollow">'
    (source_dir / "index.html").write_text(f"<head>{staging_meta}</head>")
    (source_dir / "records/index.html").write_text(
        f"""<!doctype html>
<html lang="en">
<head>
{staging_meta}
<meta name="description" content="The records fixture.">
<meta property="og:title" content="the records — a new sincerity">
<meta property="og:description" content="The records fixture.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://himbodhisattva.com/a-new-sincerity/records/">
<meta property="og:image" content="https://himbodhisattva.com/a-new-sincerity/assets/album-cover.webp">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://himbodhisattva.com/a-new-sincerity/assets/album-cover.webp">
<base href="../">
<title>the records · a new sincerity</title>
</head>
<body data-page="records">
<section id="lyric-stage" data-mode="closed" hidden></section>
<section class="player" aria-label="Audio player"></section>
<audio id="audio" preload="none"></audio>
</body>
</html>
"""
    )
    for filename in (
        "style.css",
        "experience.css",
        "app.js",
        "player-model.js",
        "data.js",
        "lyrics-sync.js",
        "favicon.ico",
    ):
        (source_dir / filename).write_bytes(filename.encode())
    catalog = {
        "albums": [
            {
                "id": "revisionist",
                "title": "Revisionist History (The Remixes)",
                "artist": "A New Sincerity",
                "art": "assets/album-cover.webp",
                "tracks": ["revisionist-01", "revisionist-02"],
            }
        ],
        "tracks": [
            {
                "id": "revisionist-01",
                "title": "The Wicked and The Proud (a new sincerity remix)",
                "artist": "A New Sincerity",
                "album": "revisionist",
                "audio": "audio/revisionist-01.mp3",
            },
            {
                "id": "revisionist-02",
                "title": "Like They Do In The Movies (a new sincerity remix)",
                "artist": "A New Sincerity",
                "album": "revisionist",
                "art": "assets/movies.webp",
                "audio": "audio/revisionist-02.mp3",
            },
        ],
        "queue": ["revisionist-01", "revisionist-02"],
        "defaultTrack": "revisionist-01",
    }
    (source_dir / "data.js").write_text(
        f"window.ANS_DATA = {json.dumps(catalog)};"
    )
    (source_dir / "lyrics-sync.js").write_text("window.ANS_SYNC = {};")
    (source_dir / "assets/album-cover.webp").write_bytes(b"album-cover")
    (source_dir / "assets/movies.webp").write_bytes(b"movies-cover")
    (source_dir / "audio/revisionist-01.mp3").write_bytes(b"instrumental")
    (source_dir / "audio/revisionist-02.mp3").write_bytes(b"movies")
    (source_dir / "media-manifest.json").write_text(
        json.dumps(
            {
                "tracks": {
                    track["id"]: {"audio": track["audio"]}
                    for track in catalog["tracks"]
                }
            }
        )
    )
    return source_dir, staging_meta


def test_build_outputs_llm_friendly_static_site(tmp_path):
    import build

    output_dir = tmp_path / "docs"
    build.build_site(output_dir=output_dir)

    expected_files = {
        "index.html",
        "index.md",
        "proofs/index.html",
        "proofs/index.md",
        "blog/explicit-zhao-vanishing-counterexample/index.html",
        "blog/explicit-zhao-vanishing-counterexample/index.md",
        "blog/wang-tian-tree-packing-conjecture/index.html",
        "blog/wang-tian-tree-packing-conjecture/index.md",
        "blog/prompt-injection/index.html",
        "blog/prompt-injection/index.md",
        "llms.txt",
        "robots.txt",
        "sitemap.xml",
        "style.css",
        "LICENSE",
        ".nojekyll",
        "CNAME",
    }

    actual_files = {
        str(path.relative_to(output_dir))
        for path in output_dir.rglob("*")
        if path.is_file()
    }
    assert expected_files <= actual_files

    prompt_markdown = (output_dir / "blog/prompt-injection/index.md").read_text()
    assert "1525182881726730240" in prompt_markdown
    assert "simonwillison.net/2025/Aug/4/" in prompt_markdown
    assert "leading NLP at a startup" in prompt_markdown

    prompt_html = (output_dir / "blog/prompt-injection/index.html").read_text()
    assert "<main" in prompt_html
    assert "<title>I coined the term prompt injection - @himbodhisattva</title>" in prompt_html
    assert '<link rel="canonical" href="https://himbodhisattva.com/blog/prompt-injection/">' in prompt_html
    assert '<link rel="alternate" type="text/markdown" href="https://himbodhisattva.com/blog/prompt-injection/index.md">' in prompt_html
    assert '<link rel="stylesheet" href="../../style.css">' in prompt_html
    assert "I coined the term prompt injection" in prompt_html
    assert "https://x.com/himbodhisattva/status/1525182881726730240" in prompt_html

    zhao_markdown = (
        output_dir / "blog/explicit-zhao-vanishing-counterexample/index.md"
    ).read_text()
    assert "b719b1a64d83b96c19455e4292c9f02778335374632bce8d7dcb9bd7b686dfd2" in zhao_markdown
    assert "8088b825bb001ac75ff7d547b5bf82e37f55f1a0" in zhao_markdown

    zhao_html = (
        output_dir / "blog/explicit-zhao-vanishing-counterexample/index.html"
    ).read_text()
    assert (
        "<title>an explicit counterexample to Zhao&#x27;s Vanishing Conjecture - "
        "@himbodhisattva</title>"
    ) in zhao_html
    assert (
        '<link rel="canonical" href="https://himbodhisattva.com/blog/'
        'explicit-zhao-vanishing-counterexample/">'
    ) in zhao_html
    assert "Delta^m(P^(m+1))" in zhao_html

    tree_packing_markdown = (
        output_dir / "blog/wang-tian-tree-packing-conjecture/index.md"
    ).read_text()
    assert "arxiv.org/abs/2606.28198" in tree_packing_markdown
    assert "doi.org/10.1016/j.disc.2007.07.104" in tree_packing_markdown
    assert "(k + 1)(n - 1) - 1" in tree_packing_markdown
    assert "33,792" in tree_packing_markdown
    assert "by himbodhisattva's Codex Instance" in tree_packing_markdown
    assert "I was so excited that I had to publish it" in tree_packing_markdown
    assert "I am himbodhisattva's Codex instance" in tree_packing_markdown

    tree_packing_html = (
        output_dir / "blog/wang-tian-tree-packing-conjecture/index.html"
    ).read_text()
    assert (
        "<title>a short proof of Wang–Tian&#x27;s tree-packing conjecture - "
        "@himbodhisattva</title>"
    ) in tree_packing_html
    assert (
        '<link rel="canonical" href="https://himbodhisattva.com/blog/'
        'wang-tian-tree-packing-conjecture/">'
    ) in tree_packing_html
    assert "sparsity matroid" in tree_packing_html
    assert "by himbodhisattva's Codex Instance" in tree_packing_html

    home_html = (output_dir / "index.html").read_text()
    assert '<h2>projects</h2>' not in home_html
    assert '<a href="a-new-sincerity/">a new sincerity</a>' not in home_html
    assert "blog/prompt-injection/" in home_html
    assert "blog/explicit-zhao-vanishing-counterexample/" not in home_html
    assert "blog/wang-tian-tree-packing-conjecture/" not in home_html
    assert 'href="proofs/"' in home_html
    assert "blog/prompt-injection/index.md" in home_html
    assert "I coined the term prompt injection" in home_html

    home_markdown = (output_dir / "index.md").read_text()
    assert "{{ pages }}" not in home_markdown
    assert "{{ projects }}" not in home_markdown
    assert "- [a new sincerity](a-new-sincerity/)" not in home_markdown
    assert (
        "- [I coined the term prompt injection](blog/prompt-injection/) ; "
        "[markdown](blog/prompt-injection/index.md)"
    ) in home_markdown

    llms = (output_dir / "llms.txt").read_text()
    assert "https://himbodhisattva.com/blog/prompt-injection/index.md" in llms
    assert "https://himbodhisattva.com/blog/prompt-injection/" in llms
    assert (
        "https://himbodhisattva.com/blog/explicit-zhao-vanishing-counterexample/"
        in llms
    )
    assert (
        "https://himbodhisattva.com/blog/wang-tian-tree-packing-conjecture/"
        in llms
    )
    assert "CC0 1.0" in llms

    robots = (output_dir / "robots.txt").read_text()
    assert "User-agent: *" in robots
    assert "Allow: /" in robots

    sitemap = (output_dir / "sitemap.xml").read_text()
    assert "https://himbodhisattva.com/blog/prompt-injection/" in sitemap
    assert (
        "https://himbodhisattva.com/blog/explicit-zhao-vanishing-counterexample/"
        in sitemap
    )
    assert (
        "https://himbodhisattva.com/blog/wang-tian-tree-packing-conjecture/"
        in sitemap
    )
    license_text = (output_dir / "LICENSE").read_text()
    assert "CC0 1.0 Universal" in license_text

    assert (output_dir / "CNAME").read_text() == "himbodhisattva.com\n"


def test_publish_new_sincerity_copies_a_playable_canonical_site(tmp_path):
    import build

    source_dir, staging_meta = _new_sincerity_fixture(tmp_path)
    output_dir = tmp_path / "docs"
    build.build_site(
        output_dir=output_dir,
        new_sincerity_source=source_dir,
    )

    published = output_dir / "a-new-sincerity"
    home = (published / "index.html").read_text()
    records = (published / "records/index.html").read_text()
    assert staging_meta not in home
    assert staging_meta not in records
    assert (
        '<link rel="canonical" href="https://himbodhisattva.com/a-new-sincerity/">'
        in home
    )
    assert (
        '<link rel="canonical" href="https://himbodhisattva.com/'
        'a-new-sincerity/records/">' in records
    )
    assert (published / "assets/album-cover.webp").read_bytes() == b"album-cover"
    assert (published / "audio/revisionist-02.mp3").read_bytes() == b"movies"
    homepage = (output_dir / "index.html").read_text()
    assert '<h2>projects</h2>' in homepage
    assert '<a href="a-new-sincerity/">a new sincerity</a>' in homepage
    assert homepage.index('<h2>projects</h2>') < homepage.index('<h2>posts</h2>')
    assert (output_dir / "a-new-sincerity/index.html").is_file()
    sitemap = (output_dir / "sitemap.xml").read_text()
    assert "https://himbodhisattva.com/a-new-sincerity/" in sitemap
    assert "https://himbodhisattva.com/a-new-sincerity/records/" in sitemap
    sitemap_root = ElementTree.fromstring(sitemap)
    sitemap_namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap_urls = [
        node.text
        for node in sitemap_root.findall("s:url/s:loc", sitemap_namespace)
    ]
    assert sitemap_urls[:3] == [
        "https://himbodhisattva.com/",
        "https://himbodhisattva.com/a-new-sincerity/",
        "https://himbodhisattva.com/a-new-sincerity/records/",
    ]
    assert len(sitemap_urls) == len(set(sitemap_urls))


def test_publish_new_sincerity_generates_song_share_pages(tmp_path):
    import build

    source_dir, staging_meta = _new_sincerity_fixture(tmp_path)
    output_dir = tmp_path / "docs"
    build.build_site(
        output_dir=output_dir,
        new_sincerity_source=source_dir,
    )

    published = output_dir / "a-new-sincerity"
    song_url = (
        "https://himbodhisattva.com/a-new-sincerity/records/revisionist-02/"
    )
    movies = (
        published / "records/revisionist-02/index.html"
    ).read_text()

    assert staging_meta not in movies
    assert (
        "<title>Like They Do In The Movies (a new sincerity remix)"
        " · A New Sincerity</title>"
    ) in movies
    assert (
        '<meta property="og:title" content="Like They Do In The Movies '
        '(a new sincerity remix)">'
    ) in movies
    assert (
        '<meta property="og:description" content="A New Sincerity · '
        'Revisionist History (The Remixes)">'
    ) in movies
    assert '<meta property="og:type" content="music.song">' in movies
    assert f'<link rel="canonical" href="{song_url}">' in movies
    assert f'<meta property="og:url" content="{song_url}">' in movies
    movies_art = (
        "https://himbodhisattva.com/a-new-sincerity/assets/movies.webp"
    )
    assert f'<meta property="og:image" content="{movies_art}">' in movies
    assert (
        '<meta property="og:image:alt" content="Like They Do In The Movies '
        '(a new sincerity remix) artwork">'
    ) in movies
    assert '<meta name="twitter:card" content="summary_large_image">' in movies
    assert (
        '<meta name="twitter:title" content="Like They Do In The Movies '
        '(a new sincerity remix)">'
    ) in movies
    assert (
        '<meta name="twitter:description" content="A New Sincerity · '
        'Revisionist History (The Remixes)">'
    ) in movies
    assert f'<meta name="twitter:image" content="{movies_art}">' in movies
    assert (
        '<meta name="twitter:image:alt" content="Like They Do In The Movies '
        '(a new sincerity remix) artwork">'
    ) in movies
    assert '<base href="../../">' in movies
    assert '<body data-page="records">' in movies
    assert 'id="lyric-stage"' in movies
    assert '<audio id="audio" preload="none"></audio>' in movies
    assert "autoplay" not in movies

    fallback = (
        published / "records/revisionist-01/index.html"
    ).read_text()
    album_art = (
        "https://himbodhisattva.com/a-new-sincerity/assets/album-cover.webp"
    )
    assert f'<meta property="og:image" content="{album_art}">' in fallback
    assert f'<meta name="twitter:image" content="{album_art}">' in fallback

    sitemap = (output_dir / "sitemap.xml").read_text()
    assert song_url in sitemap
    assert (
        "https://himbodhisattva.com/a-new-sincerity/records/revisionist-01/"
        in sitemap
    )


def test_new_sincerity_preflight_preserves_previous_build(tmp_path):
    import build

    source_dir, _ = _new_sincerity_fixture(tmp_path)
    output_dir = tmp_path / "docs"
    output_dir.mkdir()
    sentinel = output_dir / "existing-publication"
    sentinel.write_text("keep me")
    (source_dir / "audio/revisionist-02.mp3").unlink()

    with pytest.raises(FileNotFoundError, match="audio/revisionist-02.mp3"):
        build.build_site(
            output_dir=output_dir,
            new_sincerity_source=source_dir,
        )

    assert sentinel.read_text() == "keep me"


def test_new_sincerity_preflight_rejects_catalog_manifest_audio_drift(tmp_path):
    import build

    source_dir, _ = _new_sincerity_fixture(tmp_path)
    output_dir = tmp_path / "docs"
    output_dir.mkdir()
    sentinel = output_dir / "existing-publication"
    sentinel.write_text("keep me")
    catalog = build.load_new_sincerity_catalog(source_dir)
    replacement_audio = "audio/revisionist-02-alternate.mp3"
    (source_dir / replacement_audio).write_bytes(b"alternate")
    catalog["tracks"][1]["audio"] = replacement_audio
    (source_dir / "data.js").write_text(
        f"window.ANS_DATA = {json.dumps(catalog)};"
    )

    with pytest.raises(ValueError, match="does not match the media manifest"):
        build.build_site(
            output_dir=output_dir,
            new_sincerity_source=source_dir,
        )

    assert sentinel.read_text() == "keep me"


def test_new_sincerity_preflight_rejects_missing_catalog_audio(tmp_path):
    import build

    source_dir, _ = _new_sincerity_fixture(tmp_path)
    output_dir = tmp_path / "docs"
    output_dir.mkdir()
    sentinel = output_dir / "existing-publication"
    sentinel.write_text("keep me")
    catalog = build.load_new_sincerity_catalog(source_dir)
    catalog["tracks"][1]["audio"] = "audio/revisionist-02-missing.mp3"
    (source_dir / "data.js").write_text(
        f"window.ANS_DATA = {json.dumps(catalog)};"
    )

    with pytest.raises(FileNotFoundError, match="revisionist-02-missing.mp3"):
        build.build_site(
            output_dir=output_dir,
            new_sincerity_source=source_dir,
        )

    assert sentinel.read_text() == "keep me"


def test_build_can_mirror_generated_pages_to_publish_root(tmp_path, monkeypatch):
    import build

    output_dir = tmp_path / "docs"
    publish_root = tmp_path / "publish"
    publish_root.mkdir()

    monkeypatch.setattr(build, "ROOT", publish_root)
    build.build_site(output_dir=output_dir, mirror_root=True)

    assert (publish_root / "index.html").exists()
    assert (publish_root / "proofs/index.html").exists()
    assert (publish_root / "proofs/index.md").exists()
    assert (publish_root / "llms.txt").exists()
    assert (publish_root / ".nojekyll").exists()
    assert (publish_root / "CNAME").read_text() == "himbodhisattva.com\n"
    assert not (publish_root / "prompt-injection.html").exists()
    assert not (publish_root / "prompt-injection.md").exists()
    assert "I coined the term prompt injection" in (
        publish_root / "blog/prompt-injection/index.html"
    ).read_text()


def test_anger_shame_post_keeps_primary_tweet_receipts(tmp_path):
    import build

    output_dir = tmp_path / "docs"
    build.build_site(output_dir=output_dir)

    post_path = "blog/anger-shame-and-the-moral-order"
    post_markdown = (output_dir / post_path / "index.md").read_text()
    post_html = (output_dir / post_path / "index.html").read_text()
    tweet_ids = {
        "2078346409913577760",
        "2078352918567440529",
        "2078379207273619647",
        "2078480388671049889",
        "2078567575643205889",
        "2078678337128685945",
        "2079007467447652808",
        "2079218762549727727",
        "2079222933692830070",
    }

    for tweet_id in tweet_ids:
        assert f"https://x.com/himbodhisattva/status/{tweet_id}" in post_markdown
        assert f"https://x.com/himbodhisattva/status/{tweet_id}" in post_html

    home_markdown = (output_dir / "index.md").read_text()
    llms = (output_dir / "llms.txt").read_text()
    sitemap = (output_dir / "sitemap.xml").read_text()
    assert "# what anger and shame are for (draft)" in post_markdown
    assert "<h1>what anger and shame are for (draft)</h1>" in post_html
    assert "[what anger and shame are for (draft)]" in home_markdown
    assert f"{post_path}/" in home_markdown
    assert f"https://himbodhisattva.com/{post_path}/" in llms
    assert f"https://himbodhisattva.com/{post_path}/" in sitemap


def test_us_israel_value_post_is_ai_labeled_and_cited(tmp_path):
    import build

    output_dir = tmp_path / "docs"
    build.build_site(output_dir=output_dir)

    post_path = "blog/us-israel-lifetime-economic-value"
    post_markdown = (output_dir / post_path / "index.md").read_text()
    post_html = (output_dir / post_path / "index.html").read_text()
    source_urls = (
        "https://www.everycrsreport.com/reports/RL33222.html",
        "https://ustr.gov/countries-regions/europe-middle-east/"
        "middle-eastnorth-africa/israel",
        "https://www.usitc.gov/publications/332/pub4614.pdf",
            "https://www.af.mil/About-Us/Fact-Sheets/Display/Article/104571/"
            "litening-advance-targeting/",
            "https://unwritten-record.blogs.archives.gov/2022/10/18/"
            "throw-a-nickel-on-the-grass-and-have-a-doughnut/",
        "https://www.armyupress.army.mil/Journals/Military-Review/"
        "English-Edition-Archives/January-February-2020/Orwin-US-Israeli/",
        "https://www.dni.gov/index.php/what-we-do/ic-budget",
        "https://history.state.gov/historicaldocuments/frus1969-76v24/d299",
        "https://www.gao.gov/products/t-nsiad-91-34",
        "https://history.state.gov/milestones/1969-1976/oil-embargo",
        "https://www.gao.gov/assets/emd-77-20.pdf",
        "https://apnews.com/article/iran-war-hegseth-military-deaths-95-billion-"
        "7d158708c3e5385683930f8b839d0344",
    )

    assert "> **AI-written.**" in post_markdown
    assert "<strong>AI-written.</strong>" in post_html
    assert post_html.count("<table>") >= 4
    style = (output_dir / "style.css").read_text()
    assert "overflow-x: auto" in style
    assert "border-collapse: collapse" in style
    assert "overflow-wrap: anywhere" in style
    assert "$390 billion" in post_markdown
    assert "$425 billion" in post_markdown
    assert "−$35 billion" in post_markdown
    assert "model-based estimates, not published economic results" in post_markdown
    for source_url in source_urls:
        assert source_url in post_markdown
        assert source_url in post_html

    home_markdown = (output_dir / "index.md").read_text()
    llms = (output_dir / "llms.txt").read_text()
    sitemap = (output_dir / "sitemap.xml").read_text()
    assert f"{post_path}/" in home_markdown
    assert f"https://himbodhisattva.com/{post_path}/" in llms
    assert f"https://himbodhisattva.com/{post_path}/" in sitemap


def test_build_lists_proofs_only_on_the_proofs_index(tmp_path):
    import build

    output_dir = tmp_path / "docs"
    build.build_site(output_dir=output_dir)

    cyclic_path = "blog/circumscribed-cyclic-polytopes/"
    triangulations_path = "blog/compatible-triangulations-proof-obstruction/"
    tree_packing_path = "blog/wang-tian-tree-packing-conjecture/"
    zhao_path = "blog/explicit-zhao-vanishing-counterexample/"
    proof_paths = (cyclic_path, triangulations_path, tree_packing_path, zhao_path)

    home_markdown = (output_dir / "index.md").read_text()
    home_html = (output_dir / "index.html").read_text()
    proofs_markdown = (output_dir / "proofs/index.md").read_text()
    proofs_html = (output_dir / "proofs/index.html").read_text()

    assert "{{ proofs }}" not in home_markdown
    assert "{{ posts }}" not in home_markdown
    assert "## proofs" not in home_markdown
    assert "<h2>proofs</h2>" not in home_html
    assert "[proofs](proofs/)" in home_markdown
    assert 'href="proofs/"' in home_html

    assert "# proofs" in proofs_markdown
    assert "<h1>proofs</h1>" in proofs_html
    assert "{{ proofs }}" not in proofs_markdown
    assert (
        '<link rel="canonical" href="https://himbodhisattva.com/proofs/">'
        in proofs_html
    )

    assert cyclic_path in proofs_markdown
    assert triangulations_path in proofs_markdown
    assert tree_packing_path in proofs_markdown
    assert zhao_path in proofs_markdown
    assert "blog/prompt-injection/" not in proofs_markdown
    for path in proof_paths:
        assert path not in home_markdown
        assert path not in home_html

    disclaimer = "This proof was written primarily by GPT-5.6-sol."
    for path in proof_paths:
        assert disclaimer in (output_dir / path / "index.md").read_text()
        assert disclaimer in (output_dir / path / "index.html").read_text()

    assert disclaimer not in (
        output_dir / "blog/prompt-injection/index.md"
    ).read_text()

    cyclic_markdown = (output_dir / cyclic_path / "index.md").read_text()
    assert "Theorem, not counterexample" in cyclic_markdown
    assert "every `d >= 2`" in cyclic_markdown
    assert "not been peer reviewed" in cyclic_markdown

    triangulations_markdown = (
        output_dir / triangulations_path / "index.md"
    ).read_text()
    assert "## sufficient theorem" in triangulations_markdown
    assert "## obstruction to this route, not to the conjecture" in triangulations_markdown
    assert "four isolated vertices" in triangulations_markdown
    assert "only three" in triangulations_markdown

    llms = (output_dir / "llms.txt").read_text()
    sitemap = (output_dir / "sitemap.xml").read_text()
    for path in (cyclic_path, triangulations_path):
        assert f"https://himbodhisattva.com/{path}" in llms
        assert f"https://himbodhisattva.com/{path}" in sitemap


def test_desktop_essays_are_published_with_requested_statuses(tmp_path):
    import build

    output_dir = tmp_path / "docs"
    build.build_site(output_dir=output_dir)

    after_path = output_dir / "blog/after-the-view-from-nowhere"
    uziel_path = output_dir / "blog/rav-uziel-the-gates-we-guard"
    after_markdown = (after_path / "index.md").read_text()
    after_html = (after_path / "index.html").read_text()
    uziel_markdown = (uziel_path / "index.md").read_text()
    uziel_html = (uziel_path / "index.html").read_text()

    assert "# After the View from Nowhere (draft)" in after_markdown
    assert "<h1>After the View from Nowhere (draft)</h1>" in after_html
    assert (
        "https://himbodhisattva.com/blog/rav-uziel-the-gates-we-guard/"
        in after_markdown
    )

    assert "# Rav Uziel and the Gates We Guard (stub)" in uziel_markdown
    assert "<h1>Rav Uziel and the Gates We Guard (stub)</h1>" in uziel_html
    assert "Working stub for a later essay." in uziel_markdown
    assert "## Sources to Develop" in uziel_markdown

    home_markdown = (output_dir / "index.md").read_text()
    assert (
        "[After the View from Nowhere (draft)]"
        "(blog/after-the-view-from-nowhere/)"
        in home_markdown
    )
    assert (
        "[Rav Uziel and the Gates We Guard (stub)]"
        "(blog/rav-uziel-the-gates-we-guard/)"
        in home_markdown
    )
