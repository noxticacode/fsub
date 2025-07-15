from pyrogram.types import InlineKeyboardButton
from pyrogram.errors import ChatAdminRequired
from fsub import full_fsub

async def start_button(client):
    return await generate_fsub_buttons(client)

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

# Fungsi umum untuk membuat tombol fsub
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

    # Tambahkan tombol bantuan & tutup
    buttons.append([InlineKeyboardButton("📚 Bantuan", callback_data="help")])
    buttons.append([InlineKeyboardButton("🚪 Tutup", callback_data="close")])
    return buttons