from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from fsub import *


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command("batch"))
async def batch(c: Bot, message: Message):
    while True:
        try:
            first_message = await c.ask(
                text="Teruskan pesan pertama atau paste link post dari CHANNEL_DB",
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60,
            )
        except Exception:
            return
        f_msg_id = await get_message_id(c, first_message)
        if f_msg_id:
            break
        await first_message.reply(
            "Error!",
            quote=True,
        )
        continue

    while True:
        try:
            second_message = await c.ask(
                text="Teruskan pesan akhir atau paste link post dari CHANNEL_DB",
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60,
            )
        except Exception:
            return
        s_msg_id = await get_message_id(c, second_message)
        if s_msg_id:
            break
        await second_message.reply(
            "Error!",
            quote=True,
        )
        continue

    string = f"get-{f_msg_id * abs(c.db_channel.id)}-{s_msg_id * abs(c.db_channel.id)}"
    base64_string = await encode(string)
    link = f"https://t.me/{c.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔗 Buka Link", url=link)],
    [InlineKeyboardButton("📤 Bagikan ke Telegram", url=f"https://telegram.me/share/url?url={link}")]
    ])
    await second_message.reply_text(
        f"Link: {link}",
        quote=True,
        reply_markup=reply_markup,
    )