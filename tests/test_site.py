def test_build_outputs_llm_friendly_static_site(tmp_path):
    import build

    output_dir = tmp_path / "docs"
    build.build_site(output_dir=output_dir)

    expected_files = {
        "index.html",
        "index.md",
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
    assert "blog/prompt-injection/" in home_html
    assert "blog/explicit-zhao-vanishing-counterexample/" in home_html
    assert "blog/wang-tian-tree-packing-conjecture/" in home_html
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


def test_build_groups_proofs_separately_from_posts(tmp_path):
    import build

    output_dir = tmp_path / "docs"
    build.build_site(output_dir=output_dir)

    cyclic_path = "blog/circumscribed-cyclic-polytopes/"
    triangulations_path = "blog/compatible-triangulations-proof-obstruction/"
    tree_packing_path = "blog/wang-tian-tree-packing-conjecture/"
    zhao_path = "blog/explicit-zhao-vanishing-counterexample/"
    proof_paths = (cyclic_path, triangulations_path, tree_packing_path, zhao_path)

    home_markdown = (output_dir / "index.md").read_text()
    assert "{{ proofs }}" not in home_markdown
    assert "{{ posts }}" not in home_markdown
    proofs = home_markdown.split("## proofs\n", 1)[1].split("## posts\n", 1)[0]
    posts = home_markdown.split("## posts\n", 1)[1].split("## site files\n", 1)[0]

    assert cyclic_path in proofs
    assert triangulations_path in proofs
    assert tree_packing_path in proofs
    assert zhao_path in proofs
    assert cyclic_path not in posts
    assert triangulations_path not in posts
    assert tree_packing_path not in posts
    assert zhao_path not in posts
    assert "blog/prompt-injection/" in posts

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
