# Play-to-lyrics regression

Run against the local range server on the homepage and the records page.

0. With no song selected, press Play on the homepage player.
   - Playback begins with the first playable track at the top of the queue.
   - On the records page, the same action begins with the first playable track
     on the currently selected record.
1. Click a vocal track's Play button.
   - The recording starts.
   - A compact lyric panel opens above the persistent player without taking keyboard focus from the Play button.
   - Only a few lyric lines are visible.
2. Let the recording cross two cue boundaries.
   - The active line changes.
   - The lyric panel scrolls to keep that line near its center.
3. Click a visible lyric line.
   - Playback seeks to that line and the panel resumes following the song.
4. Close the lyric panel, then let the album advance naturally.
   - The next track starts and the lyric panel stays closed.
5. Start another track explicitly.
   - The new track's lyrics open in the same compact panel.
6. Start an instrumental track.
   - The panel identifies it as instrumental and shows the sleeve instead of invented lyrics.
7. Start an album near the end of a track with the lyric panel open.
   - Playback advances to the next track without interrupting the album queue.
   - The panel changes its title and cue set, then resets to the new track's opening lines.
8. Expand lyrics, then advance to another track.
   - The `#track=` URL changes to the active track.
   - Closing the full view collapses to the compact panel and clears the track URL.
9. Load a `#track=` URL directly and close it.
   - The full sleeve opens paused with a prominent Play button over the linked
     song's artwork.
   - Activating that button plays the linked song without changing the URL.
   - The prominent control disappears after playback starts, and keyboard focus
     moves to the persistent Pause control.
   - The track URL is replaced by the record URL and does not reopen on refresh.
10. Close the compact panel by keyboard.
   - Focus returns to the control that started playback, or to the persistent lyrics control if that control is gone.
11. Scroll with the keyboard or drag the lyric scrollbar.
    - Automatic following pauses and “follow the song” appears.
