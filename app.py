# app.py
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from downloader import (
    download_audio,
    download_video,
    AUDIO_DIR,
    VIDEO_DIR,
    human_size,
)

app = FastAPI(title="YouTube Downloader API")


class AudioRequest(BaseModel):
    url: str
    mode: str = "mp3"   # "mp3" atau "fast"


class VideoRequest(BaseModel):
    url: str
    quality: str = "best"  # "best" / "1080" / "720" / "480" / "360" / ...


@app.get("/")
def root():
    return {"status": "ok", "message": "YouTube Downloader API"}


@app.post("/api/audio")
def api_audio(req: AudioRequest):
    try:
        title, path, size = download_audio(req.url, mode=req.mode)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    filename = os.path.basename(path)
    return {
        "title": title,
        "size_bytes": size,
        "size_human": human_size(size),
        "download_url": f"/files/audio/{filename}",
    }


@app.post("/api/video")
def api_video(req: VideoRequest):
    try:
        title, path, size = download_video(req.url, quality=req.quality)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    filename = os.path.basename(path)
    return {
        "title": title,
        "size_bytes": size,
        "size_human": human_size(size),
        "download_url": f"/files/video/{filename}",
    }


@app.get("/files/audio/{filename}")
def get_audio(filename: str):
    path = os.path.join(AUDIO_DIR, filename)
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="File tidak ditemukan")
    return FileResponse(path, filename=filename)


@app.get("/files/video/{filename}")
def get_video(filename: str):
    path = os.path.join(VIDEO_DIR, filename)
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="File tidak ditemukan")
    return FileResponse(path, filename=filename)
