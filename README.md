# Media Downloader

Best-quality audio and video downloader built on `yt-dlp` + `ffmpeg`.

- **Audio** — the best audio stream the source offers (original, or converted to
  `m4a`, `opus`, `mp3`, or `wav`).
- **Video** — best separate video + audio streams merged with `ffmpeg`
  (no unnecessary re-encoding).

## Requirements

- Python 3.10+ (3.11+ recommended — 3.10 works but prints a yt-dlp deprecation notice)
- `ffmpeg` on your `PATH` (or a static binary placed in `env/bin/`)

## Install

```bash
python3 -m venv env
env/bin/python -m pip install -r requirements.txt
cp .env.example .env   # then edit it (see Configuration)
```

The `audio` and `video` launchers call `env/bin/python` directly, so the venv does
not need to be activated. On a non-POSIX system run
`env/bin/python download.py audio|video ...` instead.

## Configuration

Output directories come from the environment, or from the `.env` file in the repo
root (real environment variables take precedence over the file). Values support
`~` expansion.

| Variable     | Purpose             | Default    |
|--------------|---------------------|------------|
| `MUSIC_DIR`  | where audio goes    | `~/Music`  |
| `VIDEOS_DIR` | where video goes    | `~/Videos` |

On WSL, Windows folders are typically under `/mnt/<drive>/Users/<you>/...`, e.g.:

```bash
MUSIC_DIR=/mnt/c/Users/YOURUSER/Documents/Music
VIDEOS_DIR=/mnt/c/Users/YOURUSER/Videos
```

## Usage

From the repo directory:

```bash
./audio "URL"                    # best-quality audio (original, no re-encode)
./audio "URL" --format wav       # lossless PCM decode of the best audio
./video "URL"                    # best-quality video (MKV, maximum quality)
./video "URL" --container mp4    # MP4-compatible video (remux only)
./video "PLAYLIST_URL" --playlist
./audio "URL" --open             # open the output folder after downloading
```

## Options

- Audio `--format`: `best` (default), `m4a`, `opus`, `mp3`, `wav`. `mp3` encodes at
  VBR0; `wav` is a plain decode of the source audio (it does not add quality to a
  lossy source).
- Video `--container`: `mkv` (default — holds VP9/AV1/Opus/HDR without transcoding)
  or `mp4` (restricted to MP4-compatible streams so the merge stays a remux;
  high-resolution may be capped by what the source offers as MP4).
- `--playlist` — download an entire playlist (default: single video only).
- `--cookies FILE` / `--cookies-from-browser chrome` — optional authentication.
- `--open` — on WSL this opens the result in Windows Explorer via `explorer.exe`;
  elsewhere it prints the folder path.

## Notes

- Filenames are `Title [id]` and sanitized for Windows; existing files are never
  overwritten.
- If yt-dlp warns that no JavaScript runtime is available, it is harmless for now
  (full format lists are still produced). If it ever matters, install deno and pass
  `--js-runtimes deno:/path/to/deno`.
- `setup.sh` is an optional helper for the author's WSL/Ubuntu box (fixes folder
  ownership and installs system `ffmpeg` via apt); it is not needed for a fresh
  install on another machine.
