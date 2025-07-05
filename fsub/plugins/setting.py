import re
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from fsub import *

# ───── Main Settings Menu ─────
@Bot.on_message(filters.private & filters.command("settings") & filters.user(ADMINS))
async def settings_command(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👁 Disable Button", callback_data="disable")],
        [InlineKeyboardButton("🛡 Protect", callback_data="protect")],
        [InlineKeyboardButton("📝 Custom caption", callback_data="custom")],
        [InlineKeyboardButton("✅ Force Sub", callback_data="force_sub")]
    ])
    await message.reply_text("Silahkan pilih pengaturan kalian", reply_markup=keyboard)

# ───── Protect Mode ─────
@Bot.on_callback_query(filters.regex("^protect$"))
async def protect_settings(client, callback_query):
    user_id = client.me.id
    status = await get_protect(user_id)

    button = InlineKeyboardButton(
        "❌ Matikan lindungi media" if status else "✅ Aktifkan lindungi media",
        callback_data="toggle_protect"
    )

    keyboard = InlineKeyboardMarkup([
        [button],
        [InlineKeyboardButton("← Kembali", callback_data="back_to_main")]
    ])
    await callback_query.edit_message_text(
        f"Mode lindungi media: {'True' if status else 'False'}",
        reply_markup=keyboard
    )

@Bot.on_callback_query(filters.regex("^toggle_protect$"))
async def toggle_protect(client, callback_query):
    current_status = await get_protect(client.me.id)
    await set_protect(client.me.id, not current_status)
    await protect_settings(client, callback_query)

# ───── Disable Button ─────
@Bot.on_callback_query(filters.regex("^disable$"))
async def disable_settings(client, callback_query):
    status = await get_disable(client.me.id)

    button = InlineKeyboardButton(
        "❌ Matikan button media" if status else "✅ Aktifkan button media",
        callback_data="toggle_disable"
    )

    keyboard = InlineKeyboardMarkup([
        [button],
        [InlineKeyboardButton("← Kembali", callback_data="back_to_main")]
    ])

    await callback_query.edit_message_text(
        f"Mode Button media: {'True' if status else 'False'}",
        reply_markup=keyboard
    )

@Bot.on_callback_query(filters.regex("^toggle_disable$"))
async def toggle_disable(client, callback_query):
    current_status = await get_disable(client.me.id)
    await set_disable(client.me.id, not current_status)
    await disable_settings(client, callback_query)

# ───── Back to Main ─────
@Bot.on_callback_query(filters.regex("^back_to_main$"))
async def back_to_main(client, callback_query):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👁 Disable Button", callback_data="disable")],
        [InlineKeyboardButton("🛡 Protect", callback_data="protect")],
        [InlineKeyboardButton("📝 Custom caption", callback_data="custom")],
        [InlineKeyboardButton("✅ Force Sub", callback_data="force_sub")]
    ])
    await callback_query.edit_message_text("**Pilih pengaturan yang ingin Anda ubah:**", reply_markup=keyboard)

# ───── Custom Caption ─────
@Bot.on_callback_query(filters.regex("^custom$"))
async def caption_button(client, callback_query):
    try:
        isi = await client.ask(
            chat_id=callback_query.from_user.id,
            text="Silakan masukkan caption baru:\n\nKetik /batal untuk membatalkan",
            filters=filters.text,
            timeout=120
        )
        if isi.text.lower() == "/batal":
            await isi.reply("❌ Proses dibatalkan")
            return

        await add_caption(client.me.id, isi.text)
        await callback_query.edit_message_text("✅ Caption berhasil diupdate!")
    except Exception as e:
        await callback_query.edit_message_text(f"❌ Terjadi error: {e}")

# ───── Force Subscribe Menu ─────
@Bot.on_callback_query(filters.regex("^force_sub$"))
async def force_sub_menu(client, callback_query):
    button = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Tambah Channel FSub", callback_data="fsub_tambah")],
        [InlineKeyboardButton("🗑 Hapus Channel FSub", callback_data="fsub_hapus")],
        [InlineKeyboardButton("🔙 Kembali", callback_data="back_to_main")]
    ])
    await callback_query.edit_message_text("Silahkan pilih di bawah ini", reply_markup=button)

# ───── Tambah Channel FSub ─────
@Bot.on_callback_query(filters.regex("^fsub_tambah$"))
async def add_fsub_channel(client, callback_query):
    await callback_query.edit_message_text(
        "**➕ Tambah Channel FSub**\n\n"
        "Kirim ID Channel (diawali -100)\nContoh: -1001234567890",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Batalkan", callback_data="force_sub")]
        ])
    )
    try:
        response = await client.ask(
            callback_query.from_user.id,
            "Ketik /batal untuk membatalkan.",
            filters=filters.text,
            timeout=120
        )
        if response.text == "/batal":
            await response.reply("❌ Proses dibatalkan")
            return

        if not re.fullmatch(r"-100\d{7,}", response.text):
            return await response.reply("❌ Format tidak valid!")

        channel_id = int(response.text)
        if await cek_fsub(channel_id):
            return await response.reply("❌ Channel sudah terdaftar")

        chat = await client.get_chat(channel_id)
        await client.export_chat_invite_link(chat.id)

        await add_fsub(channel_id)
        await callback_query.edit_message_text(
            f"✅ Channel ditambahkan: `{channel_id}` - {chat.title}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Kembali", callback_data="force_sub")]
            ])
        )
    except Exception as e:
        await callback_query.edit_message_text(f"❌ Terjadi error: {e}")

# ───── Hapus Channel FSub ─────
@Bot.on_callback_query(filters.regex("^fsub_hapus$"))
async def list_fsub_channels(client, callback_query):
    try:
        channels = await full_fsub()
        if not channels:
            return await callback_query.edit_message_text("❌ Tidak ada channel FSub yang terdaftar")

        buttons = []
        for ch_id in channels:
            try:
                chat = await client.get_chat(ch_id)
                title = chat.title
            except:
                title = "❓ Unknown"
            buttons.append([InlineKeyboardButton(f"🗑 {title}", callback_data=f"confirm_hapus_{ch_id}")])
        buttons.append([InlineKeyboardButton("🔙 Kembali", callback_data="force_sub")])

        await callback_query.edit_message_text("Pilih channel untuk dihapus:", reply_markup=InlineKeyboardMarkup(buttons))
    except Exception as e:
        await callback_query.edit_message_text(f"❌ Gagal menampilkan daftar: {e}")

@Bot.on_callback_query(filters.regex("^confirm_hapus_"))
async def confirm_delete_fsub(client, callback_query):
    try:
        channel_id = int(callback_query.data.split("_")[2])
        await callback_query.edit_message_text(
            f"⚠️ Yakin hapus channel `{channel_id}`?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Ya", callback_data=f"hapus_{channel_id}"),
                 InlineKeyboardButton("❌ Batal", callback_data="fsub_hapus")]
            ])
        )
    except Exception as e:
        await callback_query.edit_message_text(f"❌ Error saat konfirmasi: {e}")

@Bot.on_callback_query(filters.regex("^hapus_"))
async def delete_fsub_channel(client, callback_query):
    try:
        channel_id = int(callback_query.data.split("_")[1])
        if not await cek_fsub(channel_id):
            return await callback_query.edit_message_text("❌ Channel tidak ditemukan", reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Kembali", callback_data="fsub_hapus")]
            ]))
        await del_fsub(channel_id)
        await callback_query.edit_message_text(f"✅ Channel `{channel_id}` berhasil dihapus", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Kembali", callback_data="fsub_hapus")]
        ]))
    except Exception as e:
        await callback_query.edit_message_text(f"❌ Gagal menghapus: {e}")
