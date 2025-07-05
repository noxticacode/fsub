import asyncio
from pyrogram import filters
from pyrogram.errors import FloodWait, UserDeactivated, UserIsBlocked, PeerIdInvalid
from pyrogram.types import InlineKeyboardMarkup
from fsub import *

@Bot.on_message(filters.command("start") & filters.private & is_fsubs)
async def start_command(client, message):
    user_id = message.from_user.id

    if not await present_user(user_id):
        try:
            await add_user(user_id)
        except:
            pass

    text = message.text
    if len(text) <= 7:
        out = await start_button(client)
        await message.reply_text(
            text=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=f"@{message.from_user.username}" if message.from_user.username else None,
                mention=message.from_user.mention,
                id=message.from_user.id,
            ),
            reply_markup=InlineKeyboardMarkup(out),
            disable_web_page_preview=True,
            quote=True,
        )
        return

    try:
        base64_string = text.split(" ", 1)[1]
        string = await decode(base64_string)
        argument = string.split("-")

        ids = []
        db_id = abs(client.db_channel.id)

        if len(argument) == 3:
            start = int(int(argument[1]) / db_id)
            end = int(int(argument[2]) / db_id)
            ids = list(range(start, end + 1)) if start <= end else list(range(start, end - 1, -1))

        elif len(argument) == 2:
            ids = [int(int(argument[1]) / db_id)]

    except Exception:
        return

    temp_msg = await message.reply("<code>Tunggu Sebentar...</code>")
    try:
        messages = await get_messages(client, ids)
    except Exception:
        await temp_msg.edit("<b>Telah Terjadi Error </b>🥺")
        return
    await temp_msg.delete()

    # Tarik setting di luar loop
    cust = await caption_info(client.me.id)
    disable_button = await get_disable(client.me.id)
    protect_media = await get_protect(client.me.id)

    for msg in messages:
        try:
            original_caption = msg.caption.html if msg.caption else ""

            if cust and msg.document:
                try:
                    caption = cust.format(
                        previouscaption=original_caption,
                        filename=msg.document.file_name
                    )
                except Exception as e:
                    print(f"[Caption Format Error] {e}")
                    caption = original_caption
            else:
                caption = original_caption

            await msg.copy(
                chat_id=user_id,
                caption=caption,
                protect_content=protect_media,
                reply_markup=msg.reply_markup if not disable_button else None,
            )
            await asyncio.sleep(0.5)

        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                await msg.copy(
                    chat_id=user_id,
                    caption=caption,
                    protect_content=protect_media,
                    reply_markup=msg.reply_markup if not disable_button else None,
                )
            except:
                pass

        except (PeerIdInvalid, UserIsBlocked, UserDeactivated):
            return

        except Exception as e:
            print(f"[Copy Error] {e}")
            continue


@Bot.on_message(filters.command("start") & filters.private)
async def not_joined(client, message):
    buttons = await fsub_button(client, message)
    await message.reply(
        text=FORCE_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=f"@{message.from_user.username}" if message.from_user.username else None,
            mention=message.from_user.mention,
            id=message.from_user.id,
        ),
        reply_markup=InlineKeyboardMarkup(buttons),
        quote=True,
        disable_web_page_preview=True,
    )
