#!/usr/bin/env python3
"""Apply the editorial catalog decisions that are independent of media mapping."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parent.parent
path = ROOT / "data.js"
data = json.loads(re.sub(r"^window\.ANS_DATA\s*=\s*", "", path.read_text()).rstrip().removesuffix(";"))

data["byline"] = ""
data["defaultTrack"] = "victory-lap-01"
data["queue"] = [
    "victory-lap-01",
    "unfortunately-08",
    "unfortunately-02",
    "unfortunately-10",
    "unfortunately-07",
    "revisionist-02",
    "friday-girls-02",
    "friday-girls-05",
    "system-03",
]

albums = {album["id"]: album for album in data["albums"]}
canonical_albums = {
    "unfortunately": ("(Unfortunately) I know exactly what I'm doing", "A New Sincerity"),
    "friday-girls": ("this whole time?!", "friday girls"),
    "revisionist": ("Revisionist History (The Remixes)", "A New Sincerity"),
    "victory-lap": ("victory lap", "A New Sincerity"),
    "lock-haven": ("Painting a Painting", "Lock Haven"),
    "system": ("The System of the World", "The System of the World"),
}
for album_id, (title, artist) in canonical_albums.items():
    albums[album_id]["title"] = title
    albums[album_id]["artist"] = artist
albums["revisionist"]["group"] = "ans"

album_descriptions = {
    "unfortunately": "Twelve songs about being able to explain the problem without stopping it.",
    "friday-girls": "Six uncomplicated love songs, written after my daughters asked for one.",
    "revisionist": "Nine earlier songs, remade by A New Sincerity.",
    "victory-lap": "The emulated review of (unfortunately) became the next song.",
    "lock-haven": "Nine tracks from my college band, Lock Haven.",
    "system": "Eleven tracks from The System of the World.",
}
album_credits = {
    "lock-haven": "songs by Lock Haven · reconstructed with AI",
    "system": "songs by The System of the World · reconstructed with AI",
}
for album_id, description in album_descriptions.items():
    albums[album_id]["description"] = description
for album_id, credit in album_credits.items():
    albums[album_id]["credit"] = credit

notes = {
    "revisionist-02": "Our favorite on the record. The new recording brings the high guitar harmonies forward and gives the chorus room to open.",
    "unfortunately-07": "The narrator forgives himself on someone else's behalf and feels generous for doing it. It is the funniest song on the album.",
    "unfortunately-08": "The narrator catches each manipulation as he makes it, then turns that recognition into another one. Start here.",
    "friday-girls-02": "A crush begins after Friday dinner. The song lets the invitation be the whole event.",
    "friday-girls-05": "This began as a Friday Girls section inside Victory Lap. I split it into a separate recording and gave the band the full song.",
    "revisionist-03": "A New Sincerity remake of the Lock Haven song.",
    "victory-lap-01": "The opening monologue comes from an emulated Stereogum review of (unfortunately). I sampled its diagnosis and answered it inside the song.",
    "lock-haven-03": "Original Lock Haven recording.",
    "lock-haven-08": "A New Sincerity remake included with the Lock Haven recordings.",
    "system-03": "This song already celebrated loving life with your friends, whether they were hiking or starting a band. The later work continues that theme.",
}
for track in data["tracks"]:
    track["group"] = albums[track["album"]]["group"]
    track["artist"] = albums[track["album"]]["artist"]
    if track["album"] == "lock-haven":
        track["credit"] = album_credits["lock-haven"]
        track["provenance"] = (
            "A New Sincerity remake of a Lock Haven song"
            if "a new sincerity remix" in track["title"].lower()
            else "AI-assisted reconstruction of a Lock Haven recording"
        )
    elif track["album"] == "system":
        track["credit"] = album_credits["system"]
        track["provenance"] = "AI-assisted reconstruction of a recording by The System of the World"
    if track["id"] in notes:
        track["note"] = notes[track["id"]]

path.write_text("window.ANS_DATA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n")
