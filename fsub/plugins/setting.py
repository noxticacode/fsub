import re
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from fsub import *

@Bot.on_message(filters.private & filters.command("settings") & filters.user(ADMINS))
async def settings_command(client, message):
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("👁 Disable Button", callback_data="disable")],
            [InlineKeyboardButton("🛡 Protect", callback_data="protect")],
            [InlineKeyboardButton("📝 Custom caption", callback_data="custom")],
            [InlineKeyboardButton("✅ Force Sub", callback_data="force_sub")]
        ]
    )
    await message.reply_text("Silahkan pilih pengaturan kalian", reply_markup=keyboard)

@Bot.on_callback_query(filters.regex("^protect$"))
async def protect_settings(client, callback_query):
    user_id = callback_query.from_user.id
    status = await anti_info(user_id)
    
    button = InlineKeyboardButton(
        "❌ Matikan lindungi media" if status == "True" else "✅ Aktifkan lindungi media",
        callback_data="toggle_protect"
    )
    
    keyboard = InlineKeyboardMarkup([
        [button],
        [InlineKeyboardButton("← Kembali", callback_data="back_to_main")]
    ])
    
    await callback_query.edit_message_text(
        f"Mode lindungi media: {status}",
        reply_markup=keyboard
    )

@Bot.on_callback_query(filters.regex("^toggle_protect$"))
async def toggle_protect(client, callback_query):
    user_id = callback_query.from_user.id
    status = await anti_info(user_id)
    disable = await disable_info(user_id)
    
    await add_setting(user_id, disable, status != "True")
    await protect_settings(client, callback_query)

@Bot.on_callback_query(filters.regex("^disable$"))
async def disable_settings(client, callback_query):
    user_id = callback_query.from_user.id
    status = await disable_info(user_id)
    
    button = InlineKeyboardButton(
        "❌ Matikan button media" if status == "True" else "✅ Aktifkan button media",
        callback_data="toggle_disable"
    )
    
    keyboard = InlineKeyboardMarkup([
        [button],
        [InlineKeyboardButton("← Kembali", callback_data="back_to_main")]
    ])
    
    await callback_query.edit_message_text(
        f"Mode Button media: {status}",
        reply_markup=keyboard
    )

@Bot.on_callback_query(filters.regex("^toggle_disable$"))
async def toggle_disable(client, callback_query):
    user_id = callback_query.from_user.id
    status = await disable_info(user_id)
    anti = await anti_info(user_id)
    
    await add_setting(user_id, status != "True", anti)
    await disable_settings(client, callback_query)

@Bot.on_callback_query(filters.regex("^back_to_main$"))
async def back_to_main(client, callback_query):
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("👁 Disable Button", callback_data="disable")],
            [InlineKeyboardButton("🛡 Protect", callback_data="protect")],
            [InlineKeyboardButton("📝 Custom caption", callback_data="custom")],
            [InlineKeyboardButton("✅ Force Sub", callback_data="force_sub")]
        ]
    )
    await callback_query.edit_message_text("**Pilih pengaturan yang ingin Anda ubah:**", reply_markup=keyboard)

@Bot.on_callback_query(filters.regex("^custom$"))
async def caption_button(client, callback_query):
    try:
        isi: Message = await client.ask(
            chat_id=callback_query.from_user.id,
            text="Silakan masukkan pertanyaan kuis:\n\nKetik /batal untuk membatalkan",
            filters=filters.text,
            timeout=120
        )

        if isi.text == "/batal":
            await isi.reply("❌ Proses dibatalkan")
            return
            
        await add_caption(client.me.id, isi.text)
        await callback_query.edit_message_text("✅ Caption berhasil diupdate!")
    except Exception as e:
        await callback_query.edit_message_text(f"❌ Terjadi error: {e}")

@Bot.on_callback_query(filters.regex("^force_sub$"))
async def force_sub_menu(client, callback_query):
    button = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Tambah Channel FSub", callback_data="fsub_tambah")],
        [InlineKeyboardButton("🗑 Hapus Channel FSub", callback_data="fsub_hapus")],
        [InlineKeyboardButton("🔙 Kembali", callback_data="back_to_main")]
    ])

    await callback_query.edit_message_text("Silahkan pilih di bawah ini", reply_markup=button)

@Bot.on_callback_query(filters.regex("^fsub_tambah$"))
async def add_fsub_channel(client, callback_query):
    await callback_query.edit_message_text(
        "**➕ Tambah Channel FSub**\n\n"
        "Silakan kirim ID channel yang dimulai dengan -100\n"
        "Contoh: -1001234567890\n\n"
        "Ketentuan:\n"
        "1. Harus dimulai dengan -100\n"
        "2. Harus berupa angka\n"
        "3. Minimal 10 digit\n\n"
        "Ketik /batal untuk membatalkan",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Batalkan", callback_data="force_sub")]
        ])
    )

    try:
        channel_input: Message = await client.ask(
            chat_id=callback_query.message.chat.id,
            text="",
            filters=filters.text,
            timeout=120
        )

        if channel_input.text == "/batal":
            await channel_input.reply("❌ Proses dibatalkan")
            await force_sub_menu(client, callback_query)
            return

        if not re.match(r"^-100\d{7,}$", channel_input.text):
            await channel_input.reply(
                "❌ Format ID channel tidak valid!\n"
                "Harus dimulai dengan -100 diikuti angka (minimal 10 digit total)\n"
                "Contoh: -1001234567890\n\n"
                "Silakan coba lagi atau ketik /batal"
            )
            return

        channel_id = int(channel_input.text)

        if await cek_fsub(channel_id):
            await channel_input.reply(f"❌ Channel {channel_id} sudah ada di database FSub!")
            return

        try:
            chat = await client.get_chat(channel_id)
            await client.export_chat_invite_link(chat.id)
        except Exception as e:
            await channel_input.reply(
                f"❌ Gagal memverifikasi channel: {e}\n"
                "Pastikan:\n"
                "1. Channel ada\n"
                "2. Bot sudah menjadi admin di channel\n"
                "3. Bot punya izin restrict members"
            )
            return

        await add_fsub(channel_id)
        await callback_query.edit_message_text(
            f"✅ Channel berhasil ditambahkan!\n\n"
            f"ID: {channel_id}\n"
            f"Nama: {chat.title}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Kembali", callback_data="force_sub")]
            ])
        )

    except Exception as e:
        await callback_query.edit_message_text(f"❌ Terjadi error: {e}")

@Bot.on_callback_query(filters.regex("^fsub_hapus$"))
async def list_fsub_channels(client, callback_query):
    try:
        channels = await full_fsub()
        if not channels:
            await callback_query.edit_message_text("❌ Tidak ada channel FSub yang terdaftar")
            return

        buttons = []
        for channel in channels:
            chat = await client.get_chat(channel)
            xx = chat.id
            try:
                buttons.append([
                    InlineKeyboardButton(
                        f"🗑 {chat.title}",
                        callback_data=f"confirm_hapus_{xx}"
                    )
                ])
            except:
                buttons.append([
                    InlineKeyboardButton(
                        f"🗑 Error {xx}",
                        callback_data=f"confirm_hapus_{xx}"
                    )
                ])

        buttons.append([InlineKeyboardButton("🔙 Kembali", callback_data="force_sub")])

        await callback_query.edit_message_text(
            "**📋 Daftar Channel FSub**\n\n"
            "Pilih channel yang ingin dihapus:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        await callback_query.edit_message_text(f"❌ Gagal menampilkan daftar channel: {e}")

@Bot.on_callback_query(filters.regex("^confirm_hapus_"))
async def confirm_delete_fsub(client, callback_query):
    try:
        channel_id = int(callback_query.data.split("_")[2])
        
        await callback_query.edit_message_text(
            f"⚠️ **Konfirmasi Hapus Channel**\n\n"
            f"Apakah Anda yakin ingin menghapus channel:\n"
            f"ID: `{channel_id}`\n",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ Ya, Hapus", callback_data=f"hapus_{channel_id}"),
                    InlineKeyboardButton("❌ Tidak, Batal", callback_data="fsub_hapus"),
                ]
            ])
        )
    except Exception as e:
        await callback_query.edit_message_text(f"❌ Gagal memproses konfirmasi: {e}")



@Bot.on_callback_query(filters.regex("^hapus_"))
async def delete_fsub_channel(client, callback_query):
    try:
        channel_id = int(callback_query.data.split("_")[1])
        
        # Cek dulu apakah channel ada di database
        if not await cek_fsub(channel_id):
            await callback_query.edit_message_text(
                f"❌ Channel {channel_id} tidak ditemukan di database FSub",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Kembali ke Daftar", callback_data="fsub_hapus")]]
                )
            )
            return
            
        await del_fsub(channel_id)
        
        await callback_query.edit_message_text(
            f"✅ **Channel Berhasil Dihapus**\n\n"
            f"ID: `{channel_id}`\n"
            f"Channel telah dihapus dari daftar FSub.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Kembali ke Daftar", callback_data="fsub_hapus")]]
            )
        )
    except Exception as e:
        await callback_query.edit_message_text(
            f"❌ Gagal menghapus channel: {e}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Kembali ke Daftar", callback_data="fsub_hapus")]]
            )
        )