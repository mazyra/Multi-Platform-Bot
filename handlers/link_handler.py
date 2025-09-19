import os, html
from aiogram import Router
from aiogram.types import Message, FSInputFile
from config import ADMIN_ID
from utils.downloader import download_instagram_media
from utils.youtube_downloader import download_youtube_media

router = Router()

@router.message()
async def link_handler(message: Message):
    """هندلر اصلی برای اینستا، یوتیوب و fallback"""
    url = (message.text or "").strip()

    # بررسی اینکه اصلاً لینک هست یا نه
    if not (url.startswith("http://") or url.startswith("https://")):
        await message.answer("❌ این لینک یا پیام معتبر نیست.")
        return

    try:
        # اینستاگرام
        if "instagram.com" in url:
            await message.answer("⏳ در حال دریافت محتوا از اینستاگرام...")
            result = download_instagram_media(url)

        # یوتیوب
        elif "youtube.com" in url or "youtu.be" in url:
            await message.answer("⏳ در حال دریافت محتوا از یوتیوب...")
            result = download_youtube_media(url)

        # لینک ناشناخته
        else:
            await message.answer("❌ این لینک یا پیام معتبر نیست.")
            return

        # کپشن
        caption = result.get("caption", "")
        first = True

        # ارسال مدیا
        for media_path in result.get("media_files", []):
            if media_path.lower().endswith((".mp4", ".mov", ".mkv", ".avi")):
                await message.answer_video(
                    FSInputFile(media_path),
                    caption=caption if first else None
                )
            else:
                await message.answer_photo(
                    FSInputFile(media_path),
                    caption=caption if first else None
                )
            first = False
            os.remove(media_path)

        # ارسال فایل‌های صوتی
        for audio_path in result.get("audio_files", []):
            await message.answer_audio(FSInputFile(audio_path))
            os.remove(audio_path)

    except Exception as e:
        error_text = f"❌ خطا در پردازش:\n<code>{html.escape(str(e))}</code>"
        await message.bot.send_message(chat_id=ADMIN_ID, text=error_text)
        await message.answer("❌ متأسفانه مشکلی در پردازش لینک پیش آمد.")
