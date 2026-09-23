#!/usr/bin/env python3
"""Download best-quality audio or video using yt-dlp + ffmpeg.

WSL-oriented: writes straight to Windows-accessible /mnt/c paths and can open
the resulting folder in Windows Explorer via explorer.exe.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent
ENV_BIN = REPO_DIR / "env" / "bin"
YTDLP = ENV_BIN / "yt-dlp"
BUNDLED_FFMPEG = ENV_BIN / "ffmpeg"

MUSIC_DIR = Path("/mnt/c/Users/Kia/Documents/Music")
VIDEOS_DIR = Path("/mnt/c/Users/Kia/Videos")

AUDIO_FORMATS = ("best", "m4a", "opus", "mp3", "wav")
VIDEO_CONTAINERS = ("mkv", "mp4")

OUTPUT_TEMPLATE = "%(title)s [%(id)s].%(ext)s"


def error(msg):
    print(f"error: {msg}", file=sys.stderr)


def auto_ffmpeg_location():
    """Return a --ffmpeg-location value when ffmpeg is not on the system
    PATH but a bundled static binary exists in the virtual environment."""
    if shutil.which("ffmpeg") is None and BUNDLED_FFMPEG.is_file():
        return str(ENV_BIN)
    return None


def to_windows_path(path):
    """Convert a WSL /mnt/c path to a Windows path for explorer.exe."""
    try:
        out = subprocess.check_output(
            ["wslpath", "-w", str(path)], text=True, stderr=subprocess.DEVNULL
        ).strip()
        if out:
            return out
    except (OSError, subprocess.CalledProcessError):
        pass

    p = str(path)
    if p.startswith("/mnt/"):
        drive = p[5:6].upper()
        rest = p[6:].replace("/", "\\")
        return drive + ":" + rest
    return p.replace("/", "\\")


def add_common_args(p):
    p.add_argument("url", help="video or playlist URL")
    p.add_argument(
        "--playlist",
        action="store_true",
        help="download the entire playlist (default: single video only)",
    )
    p.add_argument(
        "--open",
        action="store_true",
        help="open the output folder in Windows Explorer after downloading",
    )
    p.add_argument(
        "--cookies",
        metavar="FILE",
        help="path to a cookies.txt file for authenticated downloads",
    )
    p.add_argument(
        "--cookies-from-browser",
        metavar="BROWSER",
        help="use cookies from a browser (e.g. chrome, firefox)",
    )
    p.add_argument(
        "--ffmpeg-location",
        metavar="PATH",
        help="path to the ffmpeg binary if it is not on PATH",
    )
    p.add_argument(
        "--js-runtimes",
        metavar="RUNTIME[:PATH]",
        help="yt-dlp JS runtime for YouTube extraction, e.g. deno:/path/to/deno",
    )


def build_common(cmd, args):
    if args.cookies:
        cmd += ["--cookies", args.cookies]
    if args.cookies_from_browser:
        cmd += ["--cookies-from-browser", args.cookies_from_browser]
    loc = args.ffmpeg_location or auto_ffmpeg_location()
    if loc:
        cmd += ["--ffmpeg-location", loc]
    if args.js_runtimes:
        cmd += ["--js-runtimes", args.js_runtimes]

    cmd += ["--output", OUTPUT_TEMPLATE]
    cmd += ["--windows-filenames"]
    cmd += ["--no-overwrites"]
    cmd += ["--add-metadata"]
    cmd += ["--yes-playlist" if args.playlist else "--no-playlist"]
    return cmd


def audio_command(args):
    cmd = [str(YTDLP)]
    build_common(cmd, args)
    cmd += ["--format", "bestaudio/best"]
    cmd += ["--extract-audio"]
    cmd += ["--audio-format", args.format]
    if args.format == "mp3":
        # Highest sensible VBR quality for MP3.
        cmd += ["--audio-quality", "0"]
    if args.format in ("mp3", "m4a"):
        cmd += ["--embed-thumbnail", "--convert-thumbnails", "jpg"]
    cmd += ["--paths", str(MUSIC_DIR)]
    return cmd


def video_command(args):
    cmd = [str(YTDLP)]
    build_common(cmd, args)
    if args.container == "mp4":
        # MP4-compatible streams only, so the merge is a remux, never a transcode.
        fmt = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
    else:
        # Maximum source quality: best separate video + best separate audio.
        fmt = "bestvideo*+bestaudio/best"
    cmd += ["--format", fmt]
    cmd += ["--merge-output-format", args.container]
    cmd += ["--paths", str(VIDEOS_DIR)]
    return cmd


def parse_args(argv):
    parser = argparse.ArgumentParser(
        prog="download.py",
        description="Download best-quality audio or video via yt-dlp + ffmpeg.",
    )
    sub = parser.add_subparsers(dest="mode", required=True, metavar="{audio,video}")

    audio_p = sub.add_parser("audio", help="download best-quality audio")
    audio_p.add_argument(
        "--format",
        choices=AUDIO_FORMATS,
        default="best",
        help="audio format: best (default, original/no re-encode), "
        "m4a, opus, mp3, wav",
    )
    add_common_args(audio_p)

    video_p = sub.add_parser("video", help="download best-quality video")
    video_p.add_argument(
        "--container",
        choices=VIDEO_CONTAINERS,
        default="mkv",
        help="final container: mkv (default, max quality) or mp4",
    )
    add_common_args(video_p)

    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    if not args.url.lower().startswith(("http://", "https://")):
        error(f"invalid URL: {args.url!r}")
        return 2

    if not YTDLP.exists():
        error(f"yt-dlp not found at {YTDLP}; run 'bash setup.sh' first")
        return 1

    if args.ffmpeg_location:
        loc = Path(args.ffmpeg_location)
        if not loc.is_file() and not (loc / "ffmpeg").is_file():
            error(f"ffmpeg not found at {args.ffmpeg_location}")
            return 1
    elif shutil.which("ffmpeg") is None and not BUNDLED_FFMPEG.is_file():
        error("ffmpeg not found on PATH or in env/bin; run 'bash setup.sh' to install it")
        return 1

    out_dir = MUSIC_DIR if args.mode == "audio" else VIDEOS_DIR
    if not out_dir.is_dir():
        error(f"Windows destination directory missing: {out_dir}")
        return 1
    if not os.access(out_dir, os.W_OK):
        error(f"Windows destination directory is not writable: {out_dir}")
        return 1

    cmd = audio_command(args) if args.mode == "audio" else video_command(args)
    cmd.append(args.url)

    print(f"Destination: {out_dir}")
    print("Running:", " ".join(cmd))

    try:
        proc = subprocess.run(cmd)
    except FileNotFoundError as exc:
        error(f"failed to launch yt-dlp: {exc}")
        return 1

    if proc.returncode != 0:
        error(f"yt-dlp failed with exit code {proc.returncode}")
        return proc.returncode

    if args.open:
        win = to_windows_path(out_dir)
        print(f"Opening {win} in Windows Explorer...")
        try:
            subprocess.run(["explorer.exe", win])
        except FileNotFoundError:
            print(f"Could not launch explorer.exe; open this path manually: {win}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
