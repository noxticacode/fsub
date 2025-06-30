from fsub import *
from fsub.database.data import *
from pyrogram import enums
from pyrogram.types import InlineKeyboardButton

async def start_button(client):
    fsub = await full_fsub()
    if not fsub:
        buttons = [
            [
                InlineKeyboardButton(text="📚 Bantuan", callback_data="help"),
                InlineKeyboardButton(text="🚪 Tutup", callback_data="close"),
            ],
        ]
        return buttons
    
    buttons = []
    row = []
    
    for i in range(len(fsub)):
        try:
            chat = await client.get_chat(fsub[i])
            try:
                link = await client.export_chat_invite_link(fsub[i])
            except ChatAdminRequired:
                link = f"https://t.me/{chat.username}" if chat.username else "#"
            row.append(InlineKeyboardButton(f"🔗Join {chat.title}", url=link))
            
            if len(row) == 2 or i == len(fsub) - 1:
                buttons.append(row)
                row = []
                
        except Exception as e:
            print(f"Error getting chat {fsub[i]}: {e}")
            continue
    
    buttons.append([InlineKeyboardButton(text="📚 Bantuan", callback_data="help")])
    buttons.append([InlineKeyboardButton(text="🚪 Tutup", callback_data="close")])
    
    return buttons
    
async def fsub_button(client, message):
    fsub = await full_fsub()
    buttons = []
    
    if fsub:
        row = []
        for i in range(len(fsub)):
            try:
                chat = await client.get_chat(fsub[i])
                try:
                    link = await client.export_chat_invite_link(fsub[i])
                except ChatAdminRequired:
                    link = f"https://t.me/{chat.username}" if chat.username else "#"
                row.append(InlineKeyboardButton(f"🔗Join {chat.title}", url=link))
                
                if len(row) == 2 or i == len(fsub) - 1:
                    buttons.append(row)
                    row = []
                    
            except Exception as e:
                print(f"Error getting chat {fsub[i]}: {e}")
                continue
    
    # Tambahkan tombol bantuan/tutup baik ada FSub maupun tidak
    buttons.append([InlineKeyboardButton(text="📚 Bantuan", callback_data="help")])
    buttons.append([InlineKeyboardButton(text="🚪 Tutup", callback_data="close")])
    
    if len(message.command) > 1:
        buttons.append([
            InlineKeyboardButton(
                text="🔄 Coba Lagi",
                url=f"https://t.me/{client.username}?start={message.command[1]}",
            )
        ])
    
    return buttons