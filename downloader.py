# downloader.py
import os
import math
from typing import Optional, Tuple

from yt_dlp import YoutubeDL

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "audios")
VIDEO_DIR = os.path.join(BASE_DIR, "videos")

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)


def human_size(num_bytes: Optional[float]) -> str:
    if not num_bytes or num_bytes <= 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    i = int(min(len(units) - 1, math.floor(math.log(num_bytes, 1024))))
    p = math.pow(1024, i)
    s = round(num_bytes / p, 2)
    return f"{s} {units[i]}"


def _find_latest(folder: str) -> Optional[str]:
    if not os.path.isdir(folder):
        return None
    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    if not files:
        return None
    files.sort(key=lambda f: os.path.getmtime(os.path.join(folder, f)), reverse=True)
    return os.path.join(folder, files[0])


def download_audio(url: str, mode: str = "mp3") -> Tuple[str, str, int]:
    """
    mode: 'mp3' (konversi) atau 'fast' (file asli m4a/webm)
    return: (title, filepath, size_bytes)
    """
    # ambil info dulu
    with YoutubeDL({
        "quiet": True,
        "skip_download": True,
        "no_warnings": True,
        "ignoreconfig": True,
    }) as ydl_info:
        info = ydl_info.extract_info(url, download=False)
        title = info.get("title") or url

    if mode == "mp3":
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "ignoreconfig": True,
            "format": "bestaudio/best",
            "outtmpl": os.path.join(AUDIO_DIR, "%(title)s [%(id)s].%(ext)s"),
            "prefer_ffmpeg": True,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        }
    else:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "ignoreconfig": True,
            "format": "bestaudio/best",
            "outtmpl": os.path.join(AUDIO_DIR, "%(title)s [%(id)s].%(ext)s"),
        }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    path = _find_latest(AUDIO_DIR)
    if not path:
        raise RuntimeError("File audio tidak ditemukan.")
    size = os.path.getsize(path)
    return title, path, size


def download_video(url: str, quality: str = "best") -> Tuple[str, str, int]:
    """
    quality: 'best', '1080', '720', '480', '360', dst (tinggi maksimum)
    Semua dipaksa merge ke MP4 (video+audio).
    """
    with YoutubeDL({
        "quiet": True,
        "skip_download": True,
        "no_warnings": True,
        "ignoreconfig": True,
    }) as ydl_info:
        info = ydl_info.extract_info(url, download=False)
        title = info.get("title") or url

    if quality == "best":
        fmt = "bestvideo+bestaudio/best"
    else:
        fmt = f"bestvideo[height<={quality}]+bestaudio/best/best"

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "ignoreconfig": True,
        "format": fmt,
        "merge_output_format": "mp4",
        "outtmpl": os.path.join(VIDEO_DIR, "%(title)s [%(id)s].%(ext)s"),
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    path = _find_latest(VIDEO_DIR)
    if not path:
        raise RuntimeError("File video tidak ditemukan.")
    size = os.path.getsize(path)
    return title, path, size
