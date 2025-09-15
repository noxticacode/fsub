from fsub.database.but import check_force_sub, generate_fsub_buttons

not_joined = await check_force_sub(client, message.from_user.id)
if not_joined:
    buttons = await generate_fsub_buttons(client)
    return await message.reply(
        "❌ Anda harus join semua channel berikut dulu untuk akses konten.",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
