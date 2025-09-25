# downloader.py
import os
import subprocess
from urllib.parse import urlparse, urlunparse, ParseResult

import requests
from yt_dlp import YoutubeDL
import instaloader
from config import DOWNLOAD_PATH


# -----------------------------
# Helpers
# -----------------------------
def _ensure_dirs():
    os.makedirs(DOWNLOAD_PATH, exist_ok=True)
    os.makedirs("data", exist_ok=True)

def _normalize_url(url: str) -> str:
    p = urlparse(url.strip())
    netloc = p.netloc.replace("instagram.comp", "instagram.com")
    if netloc.endswith("instagram.com") and not netloc.startswith("www."):
        netloc = "www." + netloc
    clean = ParseResult(
        scheme="https",
        netloc=netloc or "www.instagram.com",
        path=p.path,
        params="",
        query="",     # remove igsh/utm/...
        fragment="",
    )
    return urlunparse(clean)

def _shortcode_from_url(url: str) -> str | None:
    try:
        parts = urlparse(url).path.strip("/").split("/")
        if len(parts) >= 2 and parts[0] in {"p", "reel", "tv"}:
            return parts[1]
    except Exception:
        pass
    return None

def _ext_from_url(u: str, default: str) -> str:
    ext = os.path.splitext(urlparse(u).path)[1].lower()
    return ext if ext else default

def extract_audio(video_path: str) -> str | None:
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

# ---- cookies: فقط امن و ASCII-safe ----
_ALLOWED_COOKIES = {
    "sessionid", "csrftoken", "ds_user_id", "mid", "ig_did", "rur",
    "shbid", "shbts", "datr", "ig_nrcb"
}

def _load_cookies(cookiefile: str) -> dict:
    jar = {}
    try:
        with open(cookiefile, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split("\t")
                if len(parts) < 7:
                    continue
                name, value = parts[5].strip(), parts[6].strip()
                if name not in _ALLOWED_COOKIES:
                    continue
                try:
                    value.encode("latin-1")  # فقط مقادیر ASCII/latin-1
                except UnicodeEncodeError:
                    continue
                jar[name] = value
    except FileNotFoundError:
        pass
    return jar

def _build_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36",
        "Referer": "https://www.instagram.com/",
        "Accept": "*/*",
    })
    ck = _load_cookies(os.path.join("data", "cookies.txt"))
    if ck:
        s.cookies.update(ck)
    return s

def _download_with_session(s: requests.Session, url: str, outpath: str) -> None:
    with s.get(url, stream=True, timeout=40) as r:
        r.raise_for_status()
        with open(outpath, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 64):
                if chunk:
                    f.write(chunk)


# -----------------------------
# Main
# -----------------------------
def download_instagram_media(url: str) -> dict:
    """
    خروجی:
      {"media_files": [...], "audio_files": [...], "caption": "..."}
    """
    _ensure_dirs()
    media_files: list[str] = []
    audio_files: list[str] = []
    caption = ""

    url = _normalize_url(url)

    # --- Path A: yt_dlp (ویدیو/ریلز) ---
    ydl_opts = {
    "outtmpl": os.path.join(DOWNLOAD_PATH, "%(id)s.%(ext)s"),
    "format": "mp4[ext=mp4][vcodec^=avc1][acodec^=mp4a]/best[ext=mp4]",
    "merge_output_format": "mp4",
    "quiet": True,
    "cookiefile": os.path.join("data", "cookies.txt"),
}

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            caption = info.get("description", "") or info.get("title", "") or ""

            def _handle_entry(entry):
                fp = ydl.prepare_filename(entry)
                if os.path.exists(fp):
                    media_files.append(fp)
                    mp3 = extract_audio(fp)
                    if mp3:
                        audio_files.append(mp3)

            if isinstance(info, dict) and "entries" in info and info["entries"]:
                for entry in info["entries"]:
                    _handle_entry(entry)
            else:
                _handle_entry(info)

            if media_files:
                return {"media_files": media_files, "audio_files": audio_files, "caption": caption}
    except Exception:
        pass  

    
    try:
        shortcode = _shortcode_from_url(url)
        if not shortcode:
            raise RuntimeError("Cannot extract shortcode from URL")

        L = instaloader.Instaloader(
            dirname_pattern=DOWNLOAD_PATH,
            save_metadata=False,
            download_comments=False,
            post_metadata_txt_pattern="",
        )

        session = _build_session()
        L.context._session = session
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        caption = post.caption or caption

        session = _build_session()

        if post.typename == "GraphSidecar":
            for idx, node in enumerate(post.get_sidecar_nodes(), start=1):
                if node.is_video:
                    vurl = node.video_url
                    ext = _ext_from_url(vurl, ".mp4")
                    fp = os.path.join(DOWNLOAD_PATH, f"{post.shortcode}_{idx}{ext}")
                    _download_with_session(session, vurl, fp)
                    media_files.append(fp)
                    mp3 = extract_audio(fp)
                    if mp3:
                        audio_files.append(mp3)
                else:
                    iurl = node.display_url  # full-size
                    ext = _ext_from_url(iurl, ".jpg")
                    fp = os.path.join(DOWNLOAD_PATH, f"{post.shortcode}_{idx}{ext}")
                    _download_with_session(session, iurl, fp)
                    media_files.append(fp)
        else:
            if post.is_video:
                vurl = post.video_url
                ext = _ext_from_url(vurl, ".mp4")
                fp = os.path.join(DOWNLOAD_PATH, f"{post.shortcode}{ext}")
                _download_with_session(session, vurl, fp)
                media_files.append(fp)
                mp3 = extract_audio(fp)
                if mp3:
                    audio_files.append(mp3)
            else:
                iurl = post.url  # full-size
                ext = _ext_from_url(iurl, ".jpg")
                fp = os.path.join(DOWNLOAD_PATH, f"{post.shortcode}{ext}")
                _download_with_session(session, iurl, fp)
                media_files.append(fp)

        if not media_files:
            raise RuntimeError("No media found via instaloader")

        return {"media_files": media_files, "audio_files": audio_files, "caption": caption}

    except Exception as e:
        raise RuntimeError(f"خطا در دانلود عکس از اینستاگرام: {e}")

    return {"media_files": media_files, "audio_files": audio_files, "caption": caption}
