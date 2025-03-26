from sys import exit

from pyrogram import Client

from fsub.config import *
from fsub.database.data import *
from fsub.database.func import *
from fsub.database.but import *

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_id=APP_ID,
            api_hash=API_HASH,
            plugins=dict(root="fsub/plugins"),
            bot_token=BOT_TOKEN,
            in_memory=True,
        )
        self.LOGGER = LOGGER

    async def start(self):
        try:
            await super().start()
            is_bot = await self.get_me()
            self.username = is_bot.username
            self.namebot = is_bot.first_name
            self.LOGGER(__name__).info(
                f"BOT_TOKEN detected!\n"
                f"  Username: @{self.username}\n\n"
            )
        except Exception as e:
            self.LOGGER(__name__).warning(e)
            exit()
        FSUB = await full_fsub()
        if FSUB is not None:
            for channel_id in FSUB:
                try:
                    info = await self.get_chat(channel_id)
                    link = info.invite_link
                    if not link:
                        await self.export_chat_invite_link(channel_id)
                        link = info.invite_link
                    setattr(self, f"invitelink {channel_id}", link)
                    self.LOGGER(__name__).info(
                        f"FORCE_SUB {channel_id} Detected!\n"
                        f"  Title: {info.title}\n"
                        f"  Chat ID: {info.id}\n\n"
                    )
                except Exception as e:
                    self.LOGGER(__name__).warning(e)
                    self.LOGGER(__name__).warning(
                        f"Pastikan @{self.username} "
                        f"menjadi Admin di FORCE_SUB {channel_id}\n\n"
                    )
                    exit()
        else:
            self.LOGGER(__name__).info(f"Tidak ada FORCE_SUB yang dikonfigurasi")

        try:
            db_channel = await self.get_chat(CHANNEL_DB)
            self.db_channel = db_channel
            await self.send_message(chat_id=db_channel.id, text="Bot Aktif!\n\n")
            self.LOGGER(__name__).info(
                "CHANNEL_DB Detected!\n"
                f"  Title: {db_channel.title}\n"
                f"  Chat ID: {db_channel.id}\n\n"
            )
        except Exception as e:
            self.LOGGER(__name__).warning(e)
            self.LOGGER(__name__).warning(
                f"Pastikan @{self.username} "
                "menjadi Admin di CHANNEL_DB\n\n"
            )
            exit()

        self.LOGGER(__name__).info(
            "Bot Aktif!\n\n"
        )

    async def stop(self, *args):
        self.LOGGER(__name__).info("Stopping bot...")
        await super().stop()
        self.LOGGER(__name__).info("Bot Berhenti!\n\n")