# Media Downloader

Downloads to Windows-accessible folders:

- Audio: `C:\Users\Kia\Documents\Music`
- Video: `C:\Users\Kia\Videos`

Already set up: virtual environment at `env/` on a bundled Python 3.12
(`.py312`), with `yt-dlp` and a bundled static `ffmpeg`. Both launchers call
`env/bin/python` directly, so no activation needed.

## Optional finalize step (requires sudo)

Installs system `ffmpeg` so it is available on PATH:

```bash
bash /home/kia/downloads/setup.sh
```

The downloader works either way. If you skip this, run the downloader commands
below; if you run it, everything keeps working the same.

## Installing on another machine

The virtual environment (`env/`) and bundled Python (`.py312/`) are not tracked in
git. To set up fresh (e.g. after cloning), from the repository root:

```bash
python3 -m venv env                       # a system Python 3.11+ is ideal
env/bin/python -m pip install -r requirements.txt
```

Then make sure `ffmpeg` is on your PATH (e.g. `sudo apt install ffmpeg`), or drop a
static `ffmpeg` into `env/bin/`. Both launchers call `env/bin/python` directly, so no
activation is needed.

The default output folders are Windows/WSL-specific constants near the top of
`download.py` (`MUSIC_DIR` / `VIDEOS_DIR`); adjust them to suit your machine.

## Commands

```bash
# Best-quality audio (original stream, no re-encode)
./audio "YOUTUBE_URL"

# WAV (lossless decode of the best source audio)
./audio "YOUTUBE_URL" --format wav

# Best-quality video (MKV, maximum source quality, no transcode)
./video "YOUTUBE_URL"

# MP4-compatible video (remux only; may cap below 4K if only VP9/AV1 exists)
./video "YOUTUBE_URL" --container mp4

# Download a whole playlist
./video "PLAYLIST_URL" --playlist
./audio "PLAYLIST_URL" --playlist

# Open the output folder in Windows Explorer
./video "YOUTUBE_URL" --open
./audio "YOUTUBE_URL" --open
```

Run from inside `/home/kia/downloads`, or use the full path, e.g.
`/home/kia/downloads/audio "URL"`.

## Options

- Audio `--format`: `best` (default), `m4a`, `opus`, `mp3`, `wav`
  (`mp3` uses VBR0; `wav` is a straight PCM decode, not an upgrade).
- Video `--container`: `mkv` (default), `mp4`.
- Auth if ever needed: `--cookies cookies.txt` or `--cookies-from-browser chrome`.

Note: if yt-dlp prints a warning about a missing JavaScript runtime (deno), it is
harmless today; current format lists are still complete. If YouTube changes that
later, run `./download.py video URL --js-runtimes deno` after installing deno.
