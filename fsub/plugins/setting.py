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
        [InlineKeyboardButton("👑 Admin", callback_data="admin_menu")],
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
        [InlineKeyboardButton("👑 Admin", callback_data="admin_menu")],
        [InlineKeyboardButton("✅ Force Sub", callback_data="force_sub")]
    ])
    await callback_query.edit_message_text("**Pilih pengaturan yang ingin Anda ubah:**", reply_markup=keyboard)

# ───── Custom Caption ─────
@Bot.on_callback_query(filters.regex("^custom$"))
async def caption_menu(client, callback_query):
    try:
        current = await caption_info(client.me.id)
        teks = "**📝 Caption Aktif:**\n"
        teks += f"`{current}`\n\n" if current else "`(Belum ada caption)`\n\n"
        teks += "Silahkan pilih opsi caption:"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✏️ Ubah Caption", callback_data="edit_caption")],
            [InlineKeyboardButton("🗑 Hapus Caption", callback_data="hapus_caption")],
            [InlineKeyboardButton("← Kembali", callback_data="back_to_main")]
        ])
        await callback_query.edit_message_text(teks, reply_markup=keyboard)
    except Exception as e:
        await callback_query.edit_message_text(f"❌ Error: {e}")

@Bot.on_callback_query(filters.regex("^edit_caption$"))
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

@Bot.on_callback_query(filters.regex("^hapus_caption$"))
async def hapus_caption(client, callback_query):
    try:
        await delete_caption(client.me.id)
        await callback_query.edit_message_text("✅ Caption berhasil dihapus!", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("← Kembali", callback_data="back_to_main")]
        ]))
    except Exception as e:
        await callback_query.edit_message_text(f"❌ Terjadi error: {e}")

# ───── Force Subscribe Menu ─────
@Bot.on_callback_query(filters.regex("^force_sub$"))
async def force_sub_menu(client, callback_query):
    try:
        channels = await full_fsub()
        teks = "**📋 Daftar Channel FSub:**\n\n"
        buttons = []

        if not channels:
            teks += "Belum ada channel FSub yang ditambahkan.\n"
        else:
            for ch_id in channels:
                try:
                    chat = await client.get_chat(ch_id)
                    title = chat.title
                except:
                    title = "❓ Unknown"
                teks += f"📣 {title} | `{ch_id}`\n"
                buttons.append([InlineKeyboardButton("🗑 Hapus", callback_data="fsub_hapus")])

        buttons.append([InlineKeyboardButton("➕ Tambah Channel FSub", callback_data="fsub_tambah")])
        buttons.append([InlineKeyboardButton("🔙 Kembali", callback_data="back_to_main")])

        await callback_query.edit_message_text(teks, reply_markup=InlineKeyboardMarkup(buttons))
    except Exception as e:
        await callback_query.edit_message_text(f"❌ Terjadi error: {e}")

@Bot.on_callback_query(filters.regex("^fsub_tambah$"))
async def add_fsub_channel(client, callback_query):
    await callback_query.edit_message_text(
        "**➕ Tambah Channel FSub**\n\n"
        "Kirim ID Channel (diawali -100)\nContoh: -1001234567890",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Batalkan", callback_data="force_sub")]])
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
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Kembali", callback_data="force_sub")]])
        )
    except Exception as e:
        await callback_query.edit_message_text(f"❌ Terjadi error: {e}")

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
        channel_id = int(callback_query.data.split("_")[-1])
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
        channel_id = int(callback_query.data.split("_")[-1])
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

# ───── Admin Menu ─────
@Bot.on_callback_query(filters.regex("^admin_menu$"))
async def admin_menu(client, callback_query):
    try:
        admins = await all_admins()
        teks = "**📋 Daftar Admin:**\n\n"
        buttons = []

        if not admins:
            teks += "Belum ada admin yang terdaftar.\n"
        else:
            for uid in admins:
                try:
                    user = await client.get_users(uid)
                    name = user.first_name
                except:
                    name = "❓ Unknown"
                teks += f"👤 {name} | `{uid}`\n"
                buttons.append([InlineKeyboardButton("🗑 Hapus", callback_data="admin_del")])

        buttons.append([InlineKeyboardButton("➕ Tambah Admin", callback_data="admin_tambah")])
        buttons.append([InlineKeyboardButton("🔙 Kembali", callback_data="back_to_main")])

        await callback_query.edit_message_text(teks, reply_markup=InlineKeyboardMarkup(buttons))
    except Exception as e:
        await callback_query.edit_message_text(f"❌ Error: {e}")

@Bot.on_callback_query(filters.regex("^admin_tambah$"))
async def tambah_admin(client, callback_query):
    await callback_query.edit_message_text(
        "**➕ Tambah Admin**\n\nKirim ID user (bukan username)",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Batalkan", callback_data="admin_menu")]])
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

        user_id = int(response.text)
        if await is_admin(user_id):
            return await response.reply("❌ User ini sudah admin")

        await add_admin(user_id)
        await callback_query.edit_message_text(
            f"✅ User `{user_id}` berhasil ditambahkan sebagai admin.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Kembali", callback_data="admin_menu")]])
        )
    except Exception as e:
        await callback_query.edit_message_text(f"❌ Error: {e}")

@Bot.on_callback_query(filters.regex("^admin_del$"))
async def list_admins(client, callback_query):
    try:
        admins = await all_admins()
        if not admins:
            return await callback_query.edit_message_text("❌ Tidak ada admin yang terdaftar")

        buttons = []
        for uid in admins:
            try:
                user = await client.get_users(uid)
                name = user.first_name
            except:
                name = "❓ Unknown"
            buttons.append([InlineKeyboardButton(f"🗑 {name}", callback_data=f"confirm_admin_del_{uid}")])

        buttons.append([InlineKeyboardButton("🔙 Kembali", callback_data="admin_menu")])
        await callback_query.edit_message_text("Pilih admin untuk dihapus:", reply_markup=InlineKeyboardMarkup(buttons))
    except Exception as e:
        await callback_query.edit_message_text(f"❌ Error: {e}")

@Bot.on_callback_query(filters.regex("^confirm_admin_del_"))
async def confirm_hapus_admins(client, callback_query):
    try:
        user_id = int(callback_query.data.split("_")[-1])  # FIXED HERE
        await callback_query.edit_message_text(
            f"⚠️ Yakin ingin menghapus admin `{user_id}`?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Ya", callback_data=f"del_admin_{user_id}"),
                 InlineKeyboardButton("❌ Batal", callback_data="admin_hapus")]
            ])
        )
    except Exception as e:
        await callback_query.edit_message_text(f"❌ Error saat konfirmasi: {e}")

@Bot.on_callback_query(filters.regex("^del_admin_"))
async def hapus_admin(client, callback_query):
    try:
        user_id = int(callback_query.data.split("_")[-1])
        await remove_admin(user_id)
        await callback_query.edit_message_text(
            f"✅ Admin `{user_id}` berhasil dihapus.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Kembali", callback_data="admin_del")]])
        )
    except Exception as e:
        await callback_query.edit_message_text(f"❌ Error saat menghapus: {e}")
