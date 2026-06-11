def test_build_outputs_llm_friendly_static_site(tmp_path):
    import build

    output_dir = tmp_path / "docs"
    build.build_site(output_dir=output_dir)

    expected_files = {
        "index.html",
        "index.md",
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

    home_html = (output_dir / "index.html").read_text()
    assert "blog/prompt-injection/" in home_html
    assert "blog/prompt-injection/index.md" in home_html
    assert "I coined the term prompt injection" in home_html

    home_markdown = (output_dir / "index.md").read_text()
    assert "{{ pages }}" not in home_markdown
    assert (
        "- [I coined the term prompt injection](blog/prompt-injection/) ; "
        "[markdown](blog/prompt-injection/index.md)"
    ) in home_markdown

    llms = (output_dir / "llms.txt").read_text()
    assert "https://himbodhisattva.com/blog/prompt-injection/index.md" in llms
    assert "https://himbodhisattva.com/blog/prompt-injection/" in llms
    assert "CC0 1.0" in llms

    robots = (output_dir / "robots.txt").read_text()
    assert "User-agent: *" in robots
    assert "Allow: /" in robots

    sitemap = (output_dir / "sitemap.xml").read_text()
    assert "https://himbodhisattva.com/blog/prompt-injection/" in sitemap

    license_text = (output_dir / "LICENSE").read_text()
    assert "CC0 1.0 Universal" in license_text

    assert (output_dir / "CNAME").read_text() == "himbodhisattva.com\n"


def test_build_can_mirror_generated_pages_to_publish_root(tmp_path, monkeypatch):
    import build

    output_dir = tmp_path / "docs"
    publish_root = tmp_path / "publish"
    publish_root.mkdir()

    monkeypatch.setattr(build, "ROOT", publish_root)
    build.build_site(output_dir=output_dir, mirror_root=True)

    assert (publish_root / "index.html").exists()
    assert (publish_root / "llms.txt").exists()
    assert (publish_root / ".nojekyll").exists()
    assert (publish_root / "CNAME").read_text() == "himbodhisattva.com\n"
    assert not (publish_root / "prompt-injection.html").exists()
    assert not (publish_root / "prompt-injection.md").exists()
    assert "I coined the term prompt injection" in (
        publish_root / "blog/prompt-injection/index.html"
    ).read_text()
