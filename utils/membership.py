from aiogram.enums.chat_member_status import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest
from config import REQUIRED_CHANNELS, ADMIN_ID

async def check_user_membership(user_id: int, bot) -> list:
    not_joined = []
    for channel in REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status not in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
                not_joined.append(channel)
        except TelegramBadRequest as e:
            error_msg = (
                f"⚠️ خطا در بررسی عضویت\n"
                f"👤 user_id: <code>{user_id}</code>\n"
                f"📢 چنل: {channel}\n"
                f"❌ {str(e)}"
            )
            await bot.send_message(chat_id=ADMIN_ID, text=error_msg)
            not_joined.append(channel)
    return not_joined
