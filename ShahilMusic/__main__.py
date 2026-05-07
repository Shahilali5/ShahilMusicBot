import asyncio
import importlib

from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from ShahilMusic import LOGGER, app, userbot
from ShahilMusic.core.call import Shahil
from ShahilMusic.misc import sudo
from ShahilMusic.plugins import ALL_MODULES
from ShahilMusic.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS


async def init():
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error("ᴀssɪsᴛᴀɴᴛ ᴄʟɪᴇɴᴛ ᴠᴀʀɪᴀʙʟᴇs ɴᴏᴛ ᴅᴇғɪɴᴇᴅ, ᴇxɪᴛɪɴɢ...")
        exit()
    await sudo()
    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except:
        pass
    await app.start()
    for all_module in ALL_MODULES:
        importlib.import_module("ShahilMusic.plugins" + all_module)
    LOGGER("ShahilMusic.plugins").info("sᴜᴄᴄᴇssғᴜʟʟʏ ɪᴍᴘᴏʀᴛᴇᴅ ᴍᴏᴅᴜʟᴇs...")
    await userbot.start()
    await Shahil.start()
    try:
        await Shahil.stream_call("https://graph.org/file/afdf28dbb314f37cf5662-9e15b1611627026f7e.mp4")
    except NoActiveGroupCall:
        LOGGER("ShahilMusic").error(
            "ᴘʟᴇᴀsᴇ ᴛᴜʀɴ ᴏɴ ᴛʜᴇ ᴠɪᴅᴇᴏᴄʜᴀᴛ ᴏғ ʏᴏᴜʀ ʟᴏɢ ɢʀᴏᴜᴘ\ᴄʜᴀɴɴᴇʟ.\n\nsᴛᴏᴘᴘɪɴɢ ʙᴏᴛ..."
        )
        exit()
    except:
        pass
    await Shahil.decorators()
    from ShahilMusic.utils.auto_update import auto_update
    asyncio.create_task(auto_update())
    LOGGER("ShahilMusic").info(
        "ꜱʜᴀʜɪʟ ᴍᴜsɪᴄ ʙᴏᴛ ʜᴀs ʙᴇᴇɴ sᴜᴄᴄᴇssғᴜʟʟʏ sᴛᴀʀᴛᴇᴅ.\n\n@Shahil440"
    )
    await idle()
    await app.stop()
    await userbot.stop()
    LOGGER("ShahilMusic").info("sᴛᴏᴘᴘɪɴɢ sʜᴀʜɪʟ ᴍᴜsɪᴄ ʙᴏᴛ...")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())