from datetime import datetime

from pyrogram import filters
from pyrogram.types import Message

from ShahilMusic import app
from ShahilMusic.core.call import Shahil
from ShahilMusic.utils import bot_sys_stats
from ShahilMusic.utils.decorators.language import language
from ShahilMusic.utils.inline import supp_markup
from config import BANNED_USERS, PING_IMG_URL


@app.on_message(filters.command(["ping", "alive"]) & ~BANNED_USERS)
@language
async def ping_com(client, message: Message, _):
    start_time = datetime.now()

    # Send initial loading message
    initial_response = await message.reply_photo(
        photo=PING_IMG_URL,
        caption=f"🔍 Checking system status...\nPlease wait a moment, {app.mention} is running diagnostics.",
    )

    # Gather stats
    pytg_ping = await Shahil.ping()
    uptime, cpu, ram, disk = await bot_sys_stats()
    end_time = datetime.now()
    ping_time = (end_time - start_time).microseconds / 1000

    # Final caption
    caption = f"""
<b>✨ {app.mention} is Alive and Ready!</b>

<b>⚡ Bot Ping:</b> <code>{ping_time:.2f} ms</code>
<b>📡 PyTg Call Ping:</b> <code>{pytg_ping} ms</code>
<b>⏱ Uptime:</b> <code>{uptime}</code>

<b>💾 RAM Usage:</b> <code>{ram}</code>
<b>🖥 CPU Load:</b> <code>{cpu}</code>
<b>🗄 Disk:</b> <code>{disk}</code>

<b>Need help or have suggestions?</b>
Tap the button below!
"""

    await initial_response.edit_caption(
        caption=caption,
        reply_markup=supp_markup(_),
    )
