import os
from pyrogram.types import InlineKeyboardButton
from pyrogram.errors import ChatAdminRequired, UserNotParticipant
from fsub import *


# Ambil semua FORCE_SUB dari .env (dinamis)
async def full_fsub():
    fsub_list = []
    i = 1
    while True:
        val = os.getenv(f"FORCE_SUB{i}")
        if not val:
            break
        try:
            fsub_list.append(int(val))
        except ValueError:
            print(f"[FSUB] FORCE_SUB{i} bukan ID valid: {val}")
        i += 1
    return fsub_list


# Cek apakah user sudah join semua FORCE_SUB
async def check_force_sub(client, user_id: int):
    """
    Mengecek apakah user sudah join semua channel FORCE_SUB.
    Return list channel yang BELUM diikuti.
    Jika return [] berarti user sudah join semua.
    """
    fsub_chats = await full_fsub()
    not_joined = []

    for chat_id in fsub_chats:
        try:
            member = await client.get_chat_member(chat_id, user_id)
            # Kalau user kena ban, anggap belum join
            if member.status in ("kicked", "banned"):
                not_joined.append(chat_id)
        except UserNotParticipant:
            not_joined.append(chat_id)
        except Exception as e:
            print(f"[FSUB] Error cek member {chat_id}: {e}")
            continue

    return not_joined


# Tombol awal
async def start_button(client):
    return await generate_fsub_buttons(client)


# Tombol khusus FSUB retry
async def fsub_button(client, message):
    buttons = await generate_fsub_buttons(client)

    if len(message.command) > 1:
        buttons.append([
            InlineKeyboardButton(
                "🔄 Coba Lagi",
                url=f"https://t.me/{client.username}?start={message.command[1]}"
            )
        ])
    
    return buttons


# Membuat tombol join FSUB
async def generate_fsub_buttons(client):
    fsub = await full_fsub()
    buttons = []
    row = []

    if fsub:
        for chat_id in fsub:
            try:
                chat = await client.get_chat(chat_id)

                # Gunakan invite_link jika tersedia
                link = chat.invite_link
                if not link:
                    try:
                        link = await client.export_chat_invite_link(chat_id)
                    except ChatAdminRequired:
                        link = f"https://t.me/{chat.username}" if chat.username else "#"

                row.append(InlineKeyboardButton(f"🔗 Join {chat.title}", url=link))

                if len(row) == 2:
                    buttons.append(row)
                    row = []

            except Exception as e:
                print(f"[FSUB] Gagal ambil info chat {chat_id}: {e}")
                continue

        if row:
            buttons.append(row)

    # Tombol bantuan & tutup
    buttons.append([InlineKeyboardButton("📚 Bantuan", callback_data="help")])
    buttons.append([InlineKeyboardButton("🚪 Tutup", callback_data="close")])
    return buttons
