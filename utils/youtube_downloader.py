import os
import subprocess
from yt_dlp import YoutubeDL
from config import DOWNLOAD_PATH

MAX_FILESIZE_BYTES = 50 * 1024 * 1024  

def _ensure_dirs():
    os.makedirs(DOWNLOAD_PATH, exist_ok=True)

def extract_audio(video_path: str) -> str | None:
    """استخراج صدای mp3 از ویدیو اگر موجود باشد"""
    mp3_path = os.path.splitext(video_path)[0] + ".mp3"
    try:
        probe = subprocess.run(
            ["ffprobe", "-i", video_path, "-show_streams", "-select_streams", "a", "-loglevel", "error"],
            capture_output=True, text=True
        )
        if not probe.stdout.strip():
            return None
        subprocess.run(
            ["ffmpeg", "-i", video_path, "-vn", "-ab", "192k", "-ar", "44100", "-y", mp3_path],
            check=True
        )
        return mp3_path if os.path.exists(mp3_path) else None
    except Exception:
        return None

def compress_to_480p(video_path: str) -> str:
    """فشرده‌سازی ویدیو به 480p برای ارسال به تلگرام"""
    base, ext = os.path.splitext(video_path)
    compressed_path = f"{base}_480p{ext}"
    subprocess.run([
        "ffmpeg", "-i", video_path,
        "-vf", "scale=-2:480",
        "-c:v", "libx264", "-preset", "fast", "-crf", "28",
        "-c:a", "aac", "-b:a", "128k",
        "-y", compressed_path
    ], check=True)
    return compressed_path

def download_youtube_media(url: str) -> dict:
    """دانلود یوتیوب و کاهش حجم خودکار برای تلگرام"""
    _ensure_dirs()
    media_files = []
    audio_files = []
    caption = ""

    ydl_opts = {
        "outtmpl": os.path.join(DOWNLOAD_PATH, "%(id)s.%(ext)s"),
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            caption = info.get("title", "") or ""

            entries = info["entries"] if "entries" in info else [info]
            for entry in entries:
                fp = ydl.prepare_filename(entry)
                if os.path.exists(fp):
                    if os.path.getsize(fp) > MAX_FILESIZE_BYTES:
                        fp = compress_to_480p(fp)
                    media_files.append(fp)

                    mp3_path = extract_audio(fp)
                    if mp3_path:
                        audio_files.append(mp3_path)

        return {"media_files": media_files, "audio_files": audio_files, "caption": caption}

    except Exception as e:
        raise RuntimeError(f"خطا در دانلود یوتیوب: {e}")
