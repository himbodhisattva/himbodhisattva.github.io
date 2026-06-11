from pathlib import Path


def test_build_outputs_llm_friendly_static_site(tmp_path):
    import build

    output_dir = tmp_path / "docs"
    build.build_site(output_dir=output_dir)

    expected_files = {
        "index.html",
        "index.md",
        "prompt-injection.html",
        "prompt-injection.md",
        "llms.txt",
        "robots.txt",
        "sitemap.xml",
        "style.css",
        "LICENSE",
    }

    assert expected_files <= {path.name for path in output_dir.iterdir()}

    prompt_markdown = (output_dir / "prompt-injection.md").read_text()
    assert "@himbodhisattva" in prompt_markdown
    assert "1525182881726730240" in prompt_markdown
    assert "simonwillison.net/2025/Aug/4/" in prompt_markdown

    prompt_html = (output_dir / "prompt-injection.html").read_text()
    assert "<main" in prompt_html
    assert "I coined the term prompt injection" in prompt_html
    assert "https://x.com/himbodhisattva/status/1525182881726730240" in prompt_html

    llms = (output_dir / "llms.txt").read_text()
    assert "https://himbodhisattva.github.io/prompt-injection.md" in llms
    assert "CC0 1.0" in llms

    robots = (output_dir / "robots.txt").read_text()
    assert "User-agent: *" in robots
    assert "Allow: /" in robots

    license_text = (output_dir / "LICENSE").read_text()
    assert "CC0 1.0 Universal" in license_text
