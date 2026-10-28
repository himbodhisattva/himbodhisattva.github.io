#!/usr/bin/env python3
"""Regression tests for non-destructive partial lyric-sync generation."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from tempfile import TemporaryDirectory
import json

ROOT = Path(__file__).resolve().parent.parent
spec = spec_from_file_location("generate_lyric_sync", ROOT / "tools" / "generate_lyric_sync.py")
module = module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(module)

with TemporaryDirectory() as directory:
    path = Path(directory) / "lyrics-sync.js"
    original = {"first": {"cues": [1]}, "second": {"cues": [2]}}
    path.write_text(module.SYNC_PREFIX + json.dumps(original) + ";\n")
    loaded = module.load_sync(path)
    merged = module.merge_sync(loaded, {"second": {"cues": [20]}}, ["first", "second"])
    assert merged == {"first": {"cues": [1]}, "second": {"cues": [20]}}, merged

print("PASS: partial lyric-sync updates preserve unselected tracks.")
