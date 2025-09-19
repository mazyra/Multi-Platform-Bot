import os
import html
from aiogram import Router
from aiogram.types import Message, FSInputFile
from urllib.parse import urlparse
from config import ADMIN_ID
from utils.youtube_downloader import download_youtube_media

router = Router()

@router.message()
async def handle_youtube_content(message: Message):
    url = (message.text or "").strip()
    parsed = urlparse(url.lower())

    # فقط لینک‌های یوتیوب
    if "youtube.com" not in parsed.netloc and "youtu.be" not in parsed.netloc:
        return

    await message.answer("⏳ در حال دریافت محتوا از یوتیوب...")

    try:
        result = download_youtube_media(url)
        caption = result.get("caption", "")
        first = True

        # ارسال ویدیوها
        for media_path in result.get("media_files", []):
            if os.path.exists(media_path):
                await message.answer_video(
                    FSInputFile(media_path),
                    caption=caption if first else None
                )
                first = False
                os.remove(media_path)

        # ارسال فایل‌های صوتی
        for audio_path in result.get("audio_files", []):
            if os.path.exists(audio_path):
                await message.answer_audio(FSInputFile(audio_path))
                os.remove(audio_path)

    except Exception as e:
        error_text = f"❌ خطا در پردازش یوتیوب:\n<code>{html.escape(str(e))}</code>"
        await message.bot.send_message(chat_id=ADMIN_ID, text=error_text)
        await message.answer("❌ مشکلی در پردازش لینک یوتیوب پیش آمد.")
