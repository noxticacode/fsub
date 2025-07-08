import logging
import os
from dotenv import load_dotenv

from logging.handlers import RotatingFileHandler
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

API_ID = int(os.getenv("API_ID"))

API_HASH = os.getenv("API_HASH")

CHANNEL_DB = int(os.getenv("CHANNEL_DB"))

OWNER = os.getenv("OWNER", "sepolos")


START_MSG = os.getenv(
    "START_MESSAGE",
    "<b>Hello {first}</b>\n\n<b>Saya dapat menyimpan file pribadi di Channel Tertentu dan pengguna lain dapat mengaksesnya dari link khusus.</b>",
)
try:
    ADMINS = [int(x) for x in (os.getenv("ADMINS", "").split())]
except ValueError:
    raise Exception("Daftar Admin Anda tidak berisi User ID Telegram yang valid.")

FORCE_MSG = os.getenv(
    "FORCE_SUB_MESSAGE",
    "<b>Hello {first}\n\nAnda harus bergabung di Channel/Grup saya Terlebih dahulu untuk Melihat File yang saya Bagikan\n\nSilakan Join Ke Channel & Group Terlebih Dahulu</b>",
)

LOG_FILE_NAME = "logs.txt"
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] - %(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler(LOG_FILE_NAME, maxBytes=50000000, backupCount=10),
        logging.StreamHandler(),
    ],
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)