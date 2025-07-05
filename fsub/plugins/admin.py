from fsub import *
import asyncio
from pyrogram import filters
from datetime import datetime
from time import time

START_TIME = datetime.now()
START_TIME_ISO = START_TIME.replace(microsecond=0).isoformat()
TIME_DURATION_UNITS = (
    ("week", 60 * 60 * 24 * 7),
    ("day", 60**2 * 24),
    ("hour", 60**2),
    ("min", 60),
    ("sec", 1),
)


async def _human_time_duration(seconds):
    if seconds == 0:
        return "inf"
    parts = []
    for unit, div in TIME_DURATION_UNITS:
        amount, seconds = divmod(int(seconds), div)
        if amount > 0:
            parts.append(f'{amount} {unit}{"" if amount == 1 else "s"}')
    return ", ".join(parts)


@Bot.on_message(filters.command(["users", "stats"]) & filters.user(ADMINS))
async def get_users(client, message):
    msg = await client.send_message(
        chat_id=message.chat.id, 
        text="<code>🔄 Memproses data pengguna...</code>"
    )
    users = await full_userbase()
    await msg.edit(f"👥 <b>Total Pengguna Bot:</b> <code>{len(users)}</code>")


@Bot.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def send_text(client, message):
    if message.reply_to_message:
        query = await full_userbase()
        broadcast_msg = message.reply_to_message
        total = 0
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0

        pls_wait = await message.reply(
            "📢 <code>Memulai broadcast, harap tunggu...</code>"
        )
        anti = await anti_info(client.me.id)
        for chat_id in query:
            if chat_id not in ADMINS:
                try:
                    await broadcast_msg.copy(chat_id, protect_content=anti)
                    successful += 1
                except FloodWait as e:
                    await asyncio.sleep(e.value + 3)
                    await broadcast_msg.copy(chat_id, protect_content=anti)
                    successful += 1
                except (UserIsBlocked, PeerIdInvalid):
                    del_user(chat_id)
                    blocked += 1
                except UserDeactivated:
                    del_user(chat_id)
                    deleted += 1
                except Exception:
                    del_user(chat_id)
                    unsuccessful += 1
                total += 1
        status = f"""📊 <b>Hasil Broadcast</b> 📊

├ 👥 <b>Total Pengguna:</b> <code>{total}</code>
├ ✅ <b>Berhasil:</b> <code>{successful}</code>
├ ❌ <b>Gagal:</b> <code>{unsuccessful}</code>
├ ⚠️ <b>Diblokir:</b> <code>{blocked}</code>
└ 🗑️ <b>Terhapus:</b> <code>{deleted}</code>"""
        return await pls_wait.edit(status)
    else:
        msg = await message.reply(
            "⚠️ <code>Harap reply pesan yang ingin di-broadcast!</code>"
        )
        await asyncio.sleep(8)
        await msg.delete()


@Bot.on_message(filters.command("ping"))
async def ping_pong(client, m):
    start = time()
    current_time = datetime.utcnow()
    uptime_sec = (current_time - START_TIME).total_seconds()
    uptime = await _human_time_duration(int(uptime_sec))
    m_reply = await m.reply_text("🏓 <i>Menguji ping...</i>")
    delta_ping = time() - start
    await m_reply.edit_text(
        "🏓 <b>PONG!</b> 🏓\n\n"
        f"⏱️ <b>Waktu respon:</b> <code>{delta_ping * 1000:.3f}ms</code>\n"
        f"⏳ <b>Uptime:</b> <code>{uptime}</code>"
    )


@Bot.on_message(filters.command("uptime"))
async def get_uptime(client, m):
    current_time = datetime.utcnow()
    uptime_sec = (current_time - START_TIME).total_seconds()
    uptime = await _human_time_duration(int(uptime_sec))
    await m.reply_text(
        "🤖 <b>Status Bot</b> 🤖\n\n"
        f"⏳ <b>Uptime:</b> <code>{uptime}</code>\n"
        f"🕒 <b>Mulai aktif:</b> <code>{START_TIME_ISO}</code>"
    )