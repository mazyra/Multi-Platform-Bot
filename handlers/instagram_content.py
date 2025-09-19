import os, html
from aiogram import Router
from aiogram.types import Message, FSInputFile
from config import ADMIN_ID
from utils.downloader import download_instagram_media

router = Router()

@router.message()
async def handle_instagram_content(message: Message):
    url = (message.text or "").strip()

    # فقط لینک‌های اینستاگرام
    if "instagram.com" not in url:
        return

    await message.answer("⏳ در حال دریافت محتوا از اینستاگرام...")

    try:
        result = download_instagram_media(url)
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
        error_text = f"❌ خطا در پردازش اینستاگرام:\n<code>{html.escape(str(e))}</code>"
        await message.bot.send_message(chat_id=ADMIN_ID, text=error_text)
        await message.answer("❌ مشکلی در پردازش لینک اینستاگرام پیش آمد.")
