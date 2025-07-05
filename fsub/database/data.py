from tinydb import TinyDB, Query

db = TinyDB('./join_data.json')
Q = Query()

user_data = db.table('cast')
fsub = db.table('fsub')
info = db.table('info')
protect = db.table('protect')
caption_table = db.table('caption')

# --- Broadcast ---
async def present_user(user_id: int):
    return user_data.contains(Q._id == user_id)

async def add_user(user_id: int):
    user_data.insert({'_id': user_id})

async def full_userbase():
    return [doc['_id'] for doc in user_data.all()]

async def del_user(user_id: int):
    user_data.remove(Q._id == user_id)


# --- FSub ---
async def cek_fsub(chat_id: int):
    return fsub.contains(Q._id == chat_id)

async def add_fsub(chat_id: int):
    fsub.insert({'_id': chat_id})

async def full_fsub():
    return [doc['_id'] for doc in fsub.all()]

async def del_fsub(chat_id: int):
    fsub.remove(Q._id == chat_id)


# --- Info (disable) ---
async def set_disable(user_id: int, disable: bool):
    if info.contains(Q._id == user_id):
        info.update({"disable": disable}, Q._id == user_id)
    else:
        info.insert({"_id": user_id, "disable": disable})

async def get_disable(user_id: int):
    r = info.get(Q._id == user_id)
    return r.get("disable") if r else False


# --- Protect (anti) ---
async def set_protect(user_id: int, anti: bool):
    if protect.contains(Q._id == user_id):
        protect.update({"anti": anti}, Q._id == user_id)
    else:
        protect.insert({"_id": user_id, "anti": anti})

async def get_protect(user_id: int):
    r = protect.get(Q._id == user_id)
    return r.get("anti") if r else True


# --- Caption ---
async def add_caption(user_id: int, caption: str):
    if caption_table.contains(Q._id == user_id):
        caption_table.update({"caption": caption}, Q._id == user_id)
    else:
        caption_table.insert({"_id": user_id, "caption": caption})

async def caption_info(user_id: int):
    r = caption_table.get(Q._id == user_id)
    return r.get("caption") if r else None
