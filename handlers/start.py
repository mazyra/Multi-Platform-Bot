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
    await message.answer("سلام! لینک پست/ریلز/IGTV اینستاگرام یا ویدیوی یوتیوب رو بفرست تا مدیا رو برات بفرستم.")
    admin_text = (
        "🆕 <b>کاربر جدید استارت کرد</b>\n"
        f"👤 نام: {message.from_user.first_name or ''} {message.from_user.last_name or ''}\n"
        f"🔗 یوزرنیم: @{message.from_user.username or 'ندارد'}\n"
        f"🆔 آیدی عددی: <code>{user_id}</code>"
    )
    await message.bot.send_message(chat_id=ADMIN_ID, text=admin_text)


@router.message(Command("help"))
async def help_handler(message: Message):
    help_text = (
        "📌 <b>راهنمای استفاده از ربات</b>\n\n"
        "این ربات برای دریافت و ارسال ریلزهای اینستاگرام و ویدیوهای یوتیوب طراحی شده است.\n"
        "فقط کافیست لینک را برای ربات ارسال کنید.\n\n"
        "✅ دستورات موجود:\n"
        "/start - شروع استفاده از ربات\n"
        "/help - نمایش راهنما"
    )
    await message.answer(help_text)
