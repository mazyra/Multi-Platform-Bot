from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from config import ADMIN_ID, REQUIRED_CHANNELS
from utils import db
from utils.membership import check_user_membership
import html

router = Router()


@router.message(Command("start"))
async def start_handler(message: Message):
    user_id = message.from_user.id
    not_joined = await check_user_membership(user_id, message.bot)

    if not_joined:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=f"کانال {i+1}", url=f"https://t.me/{ch.lstrip('@')}")]
                for i, ch in enumerate(not_joined)
            ]
        )
        text = (
            "📢 برای استفاده از ربات، ابتدا باید در کانال‌های زیر عضو شوی:\n\n"
            "👇 روی دکمه‌ها بزن و عضو شو:\n"
            "✅ سپس دوباره /start رو بفرست."
        )
        await message.answer(text, reply_markup=keyboard)
        return

    await db.upsert_user(message.from_user)
    await message.answer(
    """👋 سلام به تو دوست عزیزم!
    به شهر دانلود خوش اومدی؛ جایی برای یه سفر بی‌دغدغه به دنیای محتوا 🚀

    📌 اینجا چه چیزایی در دسترسه؟

    📸 پست‌های اینستاگرام (تکی یا چنداسلایدی) + کپشن کامل

    🎥 ریلز همراه با کپشن و خروجی صوتی جداگانه

    🕒 استوری‌های اینستاگرام 

    ▶️ ویدیوهای کوتاه یوتیوب + کپشن و فایل صوتی جدا

    ⚠️ نکته مهم: پیج‌های پرایوت اینستاگرام فعلاً ساپورت نمی‌شن.

    ✨ آینده‌ی «شهر دانلود» روشنه؛ قراره به زودی خیلی پلتفرم‌های معروف و محبوب دیگه هم بهش اضافه بشن!

    💡 نیاز به راهنمایی داشتی؟ کافیه بزنی: /help
    حالا لینک رو بده و بقیه مسیر رو بسپار به من 😎"""
    )

    admin_text = (
        "🆕 <b>کاربر جدید استارت کرد</b>\n"
        f"👤 نام: {message.from_user.first_name or ''} {message.from_user.last_name or ''}\n"
        f"🔗 یوزرنیم: @{message.from_user.username or 'ندارد'}\n"
        f"🆔 آیدی عددی: <code>{user_id}</code>"
    )
    await message.bot.send_message(chat_id=ADMIN_ID, text=admin_text)


@router.message(Command("help","Help | راهنما"))
async def help_handler(message: Message):
    help_text = (
    "ℹ️ <b>راهنمای استفاده از شهر دانلود</b>\n\n"
    "📌 خیلی ساده‌ست:\n\n"
    "— <b>اینستاگرام</b> 📸\n"
    "1️⃣ پست/ریلز/استوری رو باز کن.\n"
    "2️⃣ روی آیکون ✈️ (اشتراک‌گذاری) یا ⋯ بزن.\n"
    "3️⃣ گزینه «Copy Link / کپی لینک» رو انتخاب کن.\n"
    "4️⃣ لینک رو برای ربات بفرست ✅\n\n"
    "— <b>یوتیوب</b> ▶️\n"
    "1️⃣ ویدیو رو باز کن.\n"
    "2️⃣ روی «Share / اشتراک‌گذاری» بزن.\n"
    "3️⃣ گزینه «Copy Link / کپی لینک» رو انتخاب کن.\n"
    "4️⃣ لینک رو بفرست ✅\n\n"
    "⚠️ پیج‌های خصوصی اینستاگرام پشتیبانی نمی‌شن.\n\n"
    "🤝 <b>پشتیبانی:</b> اگه مشکلی داشتی، سریع به ادمین پیام بده:\n"
    "👉 @Mazyraaa"
    )

    await message.answer(help_text)
