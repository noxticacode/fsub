from fsub import *
from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, Message, InlineKeyboardButton

class Data:
    HELP = """
✨ <b>Bantuan Pengguna Bot</b> ✨

<b>Perintah Umum:</b>
  /start - Memulai bot
  /help - Menampilkan pesan bantuan ini
  /ping - Memeriksa latensi bot
  /uptime - Menampilkan waktu aktif bot
"""
    HELP_AD = """
✨ <b>Bantuan Pengguna Bot</b> ✨

<b>Perintah Admin:</b>
  /settings - Untuk setting fsub dan lain-lain
  /users - Statistik pengguna 
  /sh - Untuk sh
  /eval - Untuk eval
  /batch - Membuat multi post dalam satu link
  /broadcast - Mengirim pesan siaran ke semua pengguna
"""

    close = [
        [InlineKeyboardButton("🔒 Tutup", callback_data="close")]
    ]

    mbuttons = [
        [
            InlineKeyboardButton("🆘 Bantuan", callback_data="help")
        ],
        [
            InlineKeyboardButton("❌ Tutup", callback_data="close")
        ]
    ]

    buttons = [
        [
            InlineKeyboardButton("ℹ️ Tentang", callback_data="about")
        ],
        [
            InlineKeyboardButton("❌ Tutup", callback_data="close")
        ]
    ]

    ABOUT = """
🤖 <b>Tentang Bot</b> 🤖

@{} adalah Bot untuk menyimpan postingan atau file yang dapat diakses melalui link khusus.

<b>⚙️ Teknologi:</b>
• Framework: <a href='https://docs.pyrofork.org'>Pyrofork</a>
• Basis Kode: <a href='https://github.com/CodeXBotz/File-Sharing-Bot'>File-Sharing-Man</a>
• Pengembangan Ulang: <a href='https://github.com/ArangVolte/File-Sharing'>File-Sharing</a>

🔍 Bot ini membantu Anda menyimpan dan berbagi konten dengan mudah!
"""


@Bot.on_message(filters.private & filters.incoming & filters.command("help"))
async def help(c: Bot, m: Message):
    if m.from_user.id in ADMINS:
        await c.send_message(
            m.chat.id, 
            Data.HELP_AD,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(Data.buttons),
        )
    else:
        await c.send_message(
            m.chat.id, 
            Data.HELP,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(Data.buttons),
        )


@Bot.on_callback_query(filters.regex("^about$|^help$|^close$"))
async def handler(c: Bot, query: CallbackQuery):
    data = query.data
    if data == "about":
        try:
            await query.message.edit_text(
                text=Data.ABOUT.format(c.username),
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(Data.mbuttons),
            )
        except Exception:
            pass
    elif data == "help":
        try:
            if query.from_user.id in ADMINS:
                await query.message.edit_text(
                    text=Data.HELP_AD,
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup(Data.buttons),
                )
            else:
                await query.message.edit_text(
                    text=Data.HELP,
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup(Data.buttons),
                )
        except Exception:
            pass
    elif data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except Exception:
            return
