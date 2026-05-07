import asyncio
from typing import Union

from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup
import pytgcalls
from pytgcalls import PyTgCalls
import pytgcalls.exceptions as exceptions
from pytgcalls.types import Update

# Dynamic import for version compatibility
try:
    from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
    from pytgcalls.types.input_stream.quality import HighQualityAudio, MediumQualityVideo
    from pytgcalls.types.stream import StreamAudioEnded
except (ImportError, ModuleNotFoundError):
    from pytgcalls.types import MediaStream as AudioPiped, AudioQuality, VideoQuality
    # For backward compatibility in code below
    AudioVideoPiped = AudioPiped 

import config
from ShahilMusic import LOGGER, app
from ShahilMusic.misc import db
from ShahilMusic.utils.database import (
    add_active_chat,
    add_active_video_chat,
    get_assistant,
    get_lang,
    get_loop,
    group_assistant,
    is_autoend,
    music_on,
    remove_active_chat,
    remove_active_video_chat,
    set_loop,
)
from ShahilMusic.utils.exceptions import AssistantErr
from strings import get_string

async def _get_assistant(chat_id):
    from ShahilMusic.core.userbot import assistants
    from ShahilMusic.utils.database import get_assistant
    
    assistant_id = await get_assistant(chat_id)
    if assistant_id == 1:
        return assistants[0]
    elif assistant_id == 2:
        return assistants[1]
    elif assistant_id == 3:
        return assistants[2]
    elif assistant_id == 4:
        return assistants[3]
    elif assistant_id == 5:
        return assistants[4]
    return assistants[0]

class Call(PyTgCalls):
    def __init__(self):
        self.userbot1 = Client(
            name="ShahilMusicAssistant1",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
        )
        self.one = PyTgCalls(self.userbot1)
        
        self.userbot2 = Client(
            name="ShahilMusicAssistant2",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING2),
        )
        self.two = PyTgCalls(self.userbot2)
        
        self.userbot3 = Client(
            name="ShahilMusicAssistant3",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING3),
        )
        self.three = PyTgCalls(self.userbot3)
        
        self.userbot4 = Client(
            name="ShahilMusicAssistant4",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING4),
        )
        self.four = PyTgCalls(self.userbot4)
        
        self.userbot5 = Client(
            name="ShahilMusicAssistant5",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING5),
        )
        self.five = PyTgCalls(self.userbot5)

    async def stop_stream(self, chat_id):
        assistant = await _get_assistant(chat_id)
        try:
            await assistant.leave_group_call(chat_id)
        except:
            pass
        await remove_active_chat(chat_id)
        await remove_active_video_chat(chat_id)

    async def stop_stream_force(self, chat_id):
        try:
            if config.STRING1:
                await self.one.leave_group_call(chat_id)
        except:
            pass
        try:
            if config.STRING2:
                await self.two.leave_group_call(chat_id)
        except:
            pass
        try:
            if config.STRING3:
                await self.three.leave_group_call(chat_id)
        except:
            pass
        try:
            if config.STRING4:
                await self.four.leave_group_call(chat_id)
        except:
            pass
        try:
            if config.STRING5:
                await self.five.leave_group_call(chat_id)
        except:
            pass
        await remove_active_chat(chat_id)
        await remove_active_video_chat(chat_id)

    async def change_stream(self, client, chat_id):
        from ShahilMusic.utils.stream.stream import stream
        
        check = db.get(chat_id)
        if not check:
            return await self.stop_stream(chat_id)
        
        loop = await get_loop(chat_id)
        if loop:
            for i in range(len(check)):
                check.insert(0, check[-1])
                check.pop()
        
        next_song = check[0]
        if next_song["streamtype"] == "playlist":
            pass
        
        await self.stop_stream(chat_id)

    async def join_call(
        self,
        chat_id,
        link,
        video=None,
        image=None,
    ):
        assistant = await _get_assistant(chat_id)
        
        try:
            if video:
                try:
                    from pytgcalls.types.input_stream.quality import HighQualityAudio, MediumQualityVideo
                    stream = AudioVideoPiped(
                        link,
                        audio_parameters=HighQualityAudio(),
                        video_parameters=MediumQualityVideo(),
                    )
                except:
                    from pytgcalls.types import AudioQuality, VideoQuality
                    stream = AudioPiped(
                        link,
                        audio_parameters=AudioQuality.STUDIO,
                        video_parameters=VideoQuality.HD_720P
                    )
            else:
                try:
                    from pytgcalls.types.input_stream.quality import HighQualityAudio
                    stream = AudioPiped(link, audio_parameters=HighQualityAudio())
                except:
                    from pytgcalls.types import AudioQuality
                    stream = AudioPiped(link, audio_parameters=AudioQuality.STUDIO)
        except Exception as e:
            raise AssistantErr(f"Stream Error: {e}")

        try:
            await assistant.join_group_call(
                chat_id,
                stream,
            )
        except Exception as e:
            # Handle AlreadyJoined variants in v0.9.x vs v2.x
            if "AlreadyJoined" in str(e):
                try:
                    await assistant.change_stream(chat_id, stream)
                except Exception as inner_e:
                    raise AssistantErr(f"Change Stream Error: {inner_e}")
            elif "NoActiveGroupCall" in str(e):
                raise AssistantErr("No Active Group Call Found.")
            elif "TelegramServerError" in str(e):
                raise AssistantErr("Telegram Server Error. Please try again later.")
            else:
                raise AssistantErr(f"Join Call Error: {e}")

        await add_active_chat(chat_id)
        if video:
            await add_active_video_chat(chat_id)

    async def start(self):
        LOGGER(__name__).info("Starting PyTgCalls Clients...\n")
        if config.STRING1:
            await self.one.start()
        if config.STRING2:
            await self.two.start()
        if config.STRING3:
            await self.three.start()
        if config.STRING4:
            await self.four.start()
        if config.STRING5:
            await self.five.start()

    async def decorators(self):
        clients = []
        if config.STRING1: clients.append(self.one)
        if config.STRING2: clients.append(self.two)
        if config.STRING3: clients.append(self.three)
        if config.STRING4: clients.append(self.four)
        if config.STRING5: clients.append(self.five)

        for client in clients:
            # Dynamic handler registration
            try:
                @client.on_stream_end()
                async def handler(client, update):
                    await self.change_stream(client, update.chat_id)
            except:
                pass

            try:
                @client.on_kicked()
                async def kicked_handler(client, chat_id):
                    await self.stop_stream(chat_id)
            except:
                pass

Shahil = Call()
import asyncio
from typing import Union

from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup
import pytgcalls
from pytgcalls import PyTgCalls
import pytgcalls.exceptions as exceptions
from pytgcalls.types import Update

# Dynamic import for version compatibility
try:
    from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
    from pytgcalls.types.input_stream.quality import HighQualityAudio, MediumQualityVideo
    from pytgcalls.types.stream import StreamAudioEnded
except (ImportError, ModuleNotFoundError):
    from pytgcalls.types import MediaStream as AudioPiped, AudioQuality, VideoQuality
    # For backward compatibility in code below
    AudioVideoPiped = AudioPiped 

import config
from ShahilMusic import LOGGER, app
from ShahilMusic.misc import db
from ShahilMusic.utils.database import (
    add_active_chat,
    add_active_video_chat,
    get_assistant,
    get_lang,
    get_loop,
    group_assistant,
    is_autoend,
    music_on,
    remove_active_chat,
    remove_active_video_chat,
    set_loop,
)
from ShahilMusic.utils.exceptions import AssistantErr
from strings import get_string

async def _get_assistant(chat_id):
    from ShahilMusic.core.userbot import assistants
    from ShahilMusic.utils.database import get_assistant
    
    assistant_id = await get_assistant(chat_id)
    if assistant_id == 1:
        return assistants[0]
    elif assistant_id == 2:
        return assistants[1]
    elif assistant_id == 3:
        return assistants[2]
    elif assistant_id == 4:
        return assistants[3]
    elif assistant_id == 5:
        return assistants[4]
    return assistants[0]

class Call(PyTgCalls):
    def __init__(self):
        self.userbot1 = Client(
            name="ShahilMusicAssistant1",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
        )
        self.one = PyTgCalls(self.userbot1)
        
        self.userbot2 = Client(
            name="ShahilMusicAssistant2",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING2),
        )
        self.two = PyTgCalls(self.userbot2)
        
        self.userbot3 = Client(
            name="ShahilMusicAssistant3",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING3),
        )
        self.three = PyTgCalls(self.userbot3)
        
        self.userbot4 = Client(
            name="ShahilMusicAssistant4",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING4),
        )
        self.four = PyTgCalls(self.userbot4)
        
        self.userbot5 = Client(
            name="ShahilMusicAssistant5",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING5),
        )
        self.five = PyTgCalls(self.userbot5)

    async def stop_stream(self, chat_id):
        assistant = await _get_assistant(chat_id)
        try:
            await assistant.leave_group_call(chat_id)
        except:
            pass
        await remove_active_chat(chat_id)
        await remove_active_video_chat(chat_id)

    async def stop_stream_force(self, chat_id):
        try:
            if config.STRING1:
                await self.one.leave_group_call(chat_id)
        except:
            pass
        try:
            if config.STRING2:
                await self.two.leave_group_call(chat_id)
        except:
            pass
        try:
            if config.STRING3:
                await self.three.leave_group_call(chat_id)
        except:
            pass
        try:
            if config.STRING4:
                await self.four.leave_group_call(chat_id)
        except:
            pass
        try:
            if config.STRING5:
                await self.five.leave_group_call(chat_id)
        except:
            pass
        await remove_active_chat(chat_id)
        await remove_active_video_chat(chat_id)

    async def change_stream(self, client, chat_id):
        from ShahilMusic.utils.stream.stream import stream
        
        check = db.get(chat_id)
        if not check:
            return await self.stop_stream(chat_id)
        
        loop = await get_loop(chat_id)
        if loop:
            for i in range(len(check)):
                check.insert(0, check[-1])
                check.pop()
        
        next_song = check[0]
        if next_song["streamtype"] == "playlist":
            pass
        
        await self.stop_stream(chat_id)

    async def join_call(
        self,
        chat_id,
        link,
        video=None,
        image=None,
    ):
        assistant = await _get_assistant(chat_id)
        
        try:
            if video:
                try:
                    from pytgcalls.types.input_stream.quality import HighQualityAudio, MediumQualityVideo
                    stream = AudioVideoPiped(
                        link,
                        audio_parameters=HighQualityAudio(),
                        video_parameters=MediumQualityVideo(),
                    )
                except:
                    from pytgcalls.types import AudioQuality, VideoQuality
                    stream = AudioPiped(
                        link,
                        audio_parameters=AudioQuality.STUDIO,
                        video_parameters=VideoQuality.HD_720P
                    )
            else:
                try:
                    from pytgcalls.types.input_stream.quality import HighQualityAudio
                    stream = AudioPiped(link, audio_parameters=HighQualityAudio())
                except:
                    from pytgcalls.types import AudioQuality
                    stream = AudioPiped(link, audio_parameters=AudioQuality.STUDIO)
        except Exception as e:
            raise AssistantErr(f"Stream Error: {e}")

        try:
            await assistant.join_group_call(
                chat_id,
                stream,
            )
        except Exception as e:
            # Handle AlreadyJoined variants in v0.9.x vs v2.x
            if "AlreadyJoined" in str(e):
                try:
                    await assistant.change_stream(chat_id, stream)
                except Exception as inner_e:
                    raise AssistantErr(f"Change Stream Error: {inner_e}")
            elif "NoActiveGroupCall" in str(e):
                raise AssistantErr("No Active Group Call Found.")
            elif "TelegramServerError" in str(e):
                raise AssistantErr("Telegram Server Error. Please try again later.")
            else:
                raise AssistantErr(f"Join Call Error: {e}")

        await add_active_chat(chat_id)
        if video:
            await add_active_video_chat(chat_id)

    async def start(self):
        LOGGER(__name__).info("Starting PyTgCalls Clients...\n")
        if config.STRING1:
            await self.one.start()
        if config.STRING2:
            await self.two.start()
        if config.STRING3:
            await self.three.start()
        if config.STRING4:
            await self.four.start()
        if config.STRING5:
            await self.five.start()

    async def decorators(self):
        clients = []
        if config.STRING1: clients.append(self.one)
        if config.STRING2: clients.append(self.two)
        if config.STRING3: clients.append(self.three)
        if config.STRING4: clients.append(self.four)
        if config.STRING5: clients.append(self.five)

        for client in clients:
            # Dynamic handler registration
            try:
                @client.on_stream_end()
                async def handler(client, update):
                    await self.change_stream(client, update.chat_id)
            except:
                pass

            try:
                @client.on_kicked()
                async def kicked_handler(client, chat_id):
                    await self.stop_stream(chat_id)
            except:
                pass

Shahil = Call()
import asyncio
from typing import Union

from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup
import pytgcalls
from pytgcalls import PyTgCalls
import pytgcalls.exceptions as exceptions
from pytgcalls.types import Update

# Dynamic import for version compatibility
try:
    from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
    from pytgcalls.types.input_stream.quality import HighQualityAudio, MediumQualityVideo
    from pytgcalls.types.stream import StreamAudioEnded
except (ImportError, ModuleNotFoundError):
    from pytgcalls.types import MediaStream as AudioPiped, AudioQuality, VideoQuality
    # For backward compatibility in code below
    AudioVideoPiped = AudioPiped 

import config
from ShahilMusic import LOGGER, app
from ShahilMusic.misc import db
from ShahilMusic.utils.database import (
    add_active_chat,
    add_active_video_chat,
    get_assistant,
    get_lang,
    get_loop,
    group_assistant,
    is_autoend,
    music_on,
    remove_active_chat,
    remove_active_video_chat,
    set_loop,
)
from ShahilMusic.utils.exceptions import AssistantErr
from strings import get_string

async def _get_assistant(chat_id):
    from ShahilMusic.core.userbot import assistants
    from ShahilMusic.utils.database import get_assistant
    
    assistant_id = await get_assistant(chat_id)
    if assistant_id == 1:
        return assistants[0]
    elif assistant_id == 2:
        return assistants[1]
    elif assistant_id == 3:
        return assistants[2]
    elif assistant_id == 4:
        return assistants[3]
    elif assistant_id == 5:
        return assistants[4]
    return assistants[0]

class Call(PyTgCalls):
    def __init__(self):
        self.userbot1 = Client(
            name="ShahilMusicAssistant1",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
        )
        self.one = PyTgCalls(self.userbot1)
        
        self.userbot2 = Client(
            name="ShahilMusicAssistant2",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING2),
        )
        self.two = PyTgCalls(self.userbot2)
        
        self.userbot3 = Client(
            name="ShahilMusicAssistant3",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING3),
        )
        self.three = PyTgCalls(self.userbot3)
        
        self.userbot4 = Client(
            name="ShahilMusicAssistant4",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING4),
        )
        self.four = PyTgCalls(self.userbot4)
        
        self.userbot5 = Client(
            name="ShahilMusicAssistant5",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING5),
        )
        self.five = PyTgCalls(self.userbot5)

    async def stop_stream(self, chat_id):
        assistant = await _get_assistant(chat_id)
        try:
            await assistant.leave_group_call(chat_id)
        except:
            pass
        await remove_active_chat(chat_id)
        await remove_active_video_chat(chat_id)

    async def stop_stream_force(self, chat_id):
        try:
            if config.STRING1:
                await self.one.leave_group_call(chat_id)
        except:
            pass
        try:
            if config.STRING2:
                await self.two.leave_group_call(chat_id)
        except:
            pass
        try:
            if config.STRING3:
                await self.three.leave_group_call(chat_id)
        except:
            pass
        try:
            if config.STRING4:
                await self.four.leave_group_call(chat_id)
        except:
            pass
        try:
            if config.STRING5:
                await self.five.leave_group_call(chat_id)
        except:
            pass
        await remove_active_chat(chat_id)
        await remove_active_video_chat(chat_id)

    async def change_stream(self, client, chat_id):
        from ShahilMusic.utils.stream.stream import stream
        
        check = db.get(chat_id)
        if not check:
            return await self.stop_stream(chat_id)
        
        loop = await get_loop(chat_id)
        if loop:
            for i in range(len(check)):
                check.insert(0, check[-1])
                check.pop()
        
        next_song = check[0]
        if next_song["streamtype"] == "playlist":
            pass
        
        await self.stop_stream(chat_id)

    async def join_call(
        self,
        chat_id,
        link,
        video=None,
        image=None,
    ):
        assistant = await _get_assistant(chat_id)
        
        try:
            if video:
                try:
                    from pytgcalls.types.input_stream.quality import HighQualityAudio, MediumQualityVideo
                    stream = AudioVideoPiped(
                        link,
                        audio_parameters=HighQualityAudio(),
                        video_parameters=MediumQualityVideo(),
                    )
                except:
                    from pytgcalls.types import AudioQuality, VideoQuality
                    stream = AudioPiped(
                        link,
                        audio_parameters=AudioQuality.STUDIO,
                        video_parameters=VideoQuality.HD_720P
                    )
            else:
                try:
                    from pytgcalls.types.input_stream.quality import HighQualityAudio
                    stream = AudioPiped(link, audio_parameters=HighQualityAudio())
                except:
                    from pytgcalls.types import AudioQuality
                    stream = AudioPiped(link, audio_parameters=AudioQuality.STUDIO)
        except Exception as e:
            raise AssistantErr(f"Stream Error: {e}")

        try:
            await assistant.join_group_call(
                chat_id,
                stream,
            )
        except Exception as e:
            # Handle AlreadyJoined variants in v0.9.x vs v2.x
            if "AlreadyJoined" in str(e):
                try:
                    await assistant.change_stream(chat_id, stream)
                except Exception as inner_e:
                    raise AssistantErr(f"Change Stream Error: {inner_e}")
            elif "NoActiveGroupCall" in str(e):
                raise AssistantErr("No Active Group Call Found.")
            elif "TelegramServerError" in str(e):
                raise AssistantErr("Telegram Server Error. Please try again later.")
            else:
                raise AssistantErr(f"Join Call Error: {e}")

        await add_active_chat(chat_id)
        if video:
            await add_active_video_chat(chat_id)

    async def start(self):
        LOGGER(__name__).info("Starting PyTgCalls Clients...\n")
        if config.STRING1:
            await self.one.start()
        if config.STRING2:
            await self.two.start()
        if config.STRING3:
            await self.three.start()
        if config.STRING4:
            await self.four.start()
        if config.STRING5:
            await self.five.start()

    async def decorators(self):
        clients = []
        if config.STRING1: clients.append(self.one)
        if config.STRING2: clients.append(self.two)
        if config.STRING3: clients.append(self.three)
        if config.STRING4: clients.append(self.four)
        if config.STRING5: clients.append(self.five)

        for client in clients:
            # Dynamic handler registration
            try:
                @client.on_stream_end()
                async def handler(client, update):
                    await self.change_stream(client, update.chat_id)
            except:
                pass

            try:
                @client.on_kicked()
                async def kicked_handler(client, chat_id):
                    await self.stop_stream(chat_id)
            except:
                pass

Shahil = Call()
import asyncio
from typing import Union

from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup
import pytgcalls
from pytgcalls import PyTgCalls
import pytgcalls.exceptions as exceptions
from pytgcalls.types import Update

# Dynamic import for version compatibility
try:
    from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
    from pytgcalls.types.input_stream.quality import HighQualityAudio, MediumQualityVideo
    from pytgcalls.types.stream import StreamAudioEnded
except (ImportError, ModuleNotFoundError):
    from pytgcalls.types import MediaStream as AudioPiped, AudioQuality, VideoQuality
    # For backward compatibility in code below
    AudioVideoPiped = AudioPiped 

import config
from ShahilMusic import LOGGER, app
from ShahilMusic.misc import db
from ShahilMusic.utils.database import (
    add_active_chat,
    add_active_video_chat,
    get_assistant,
    get_lang,
    get_loop,
    group_assistant,
    is_autoend,
    music_on,
    remove_active_chat,
    remove_active_video_chat,
    set_loop,
)
from ShahilMusic.utils.exceptions import AssistantErr
from strings import get_string

async def _get_assistant(chat_id):
    from ShahilMusic.core.userbot import assistants
    from ShahilMusic.utils.database import get_assistant
    
    assistant_id = await get_assistant(chat_id)
    if assistant_id == 1:
        return assistants[0]
    elif assistant_id == 2:
        return assistants[1]
    elif assistant_id == 3:
        return assistants[2]
    elif assistant_id == 4:
        return assistants[3]
    elif assistant_id == 5:
        return assistants[4]
    return assistants[0]

class Call(PyTgCalls):
    def __init__(self):
        self.userbot1 = Client(
            name="ShahilMusicAssistant1",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
        )
        self.one = PyTgCalls(self.userbot1)
        
        self.userbot2 = Client(
            name="ShahilMusicAssistant2",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING2),
        )
        self.two = PyTgCalls(self.userbot2)
        
        self.userbot3 = Client(
            name="ShahilMusicAssistant3",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING3),
        )
        self.three = PyTgCalls(self.userbot3)
        
        self.userbot4 = Client(
            name="ShahilMusicAssistant4",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING4),
        )
        self.four = PyTgCalls(self.userbot4)
        
        self.userbot5 = Client(
            name="ShahilMusicAssistant5",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING5),
        )
        self.five = PyTgCalls(self.userbot5)

    async def stop_stream(self, chat_id):
        assistant = await _get_assistant(chat_id)
        try:
            await assistant.leave_group_call(chat_id)
        except:
            pass
        await remove_active_chat(chat_id)
        await remove_active_video_chat(chat_id)

    async def stop_stream_force(self, chat_id):
        try:
            if config.STRING1:
                await self.one.leave_group_call(chat_id)
        except:
            pass
        try:
            if config.STRING2:
                await self.two.leave_group_call(chat_id)
        except:
            pass
        try:
            if config.STRING3:
                await self.three.leave_group_call(chat_id)
        except:
            pass
        try:
            if config.STRING4:
                await self.four.leave_group_call(chat_id)
        except:
            pass
        try:
            if config.STRING5:
                await self.five.leave_group_call(chat_id)
        except:
            pass
        await remove_active_chat(chat_id)
        await remove_active_video_chat(chat_id)

    async def change_stream(self, client, chat_id):
        from ShahilMusic.utils.stream.stream import stream
        
        check = db.get(chat_id)
        if not check:
            return await self.stop_stream(chat_id)
        
        loop = await get_loop(chat_id)
        if loop:
            for i in range(len(check)):
                check.insert(0, check[-1])
                check.pop()
        
        next_song = check[0]
        if next_song["streamtype"] == "playlist":
            pass
        
        await self.stop_stream(chat_id)

    async def join_call(
        self,
        chat_id,
        link,
        video=None,
        image=None,
    ):
        assistant = await _get_assistant(chat_id)
        
        try:
            if video:
                try:
                    from pytgcalls.types.input_stream.quality import HighQualityAudio, MediumQualityVideo
                    stream = AudioVideoPiped(
                        link,
                        audio_parameters=HighQualityAudio(),
                        video_parameters=MediumQualityVideo(),
                    )
                except:
                    from pytgcalls.types import AudioQuality, VideoQuality
                    stream = AudioPiped(
                        link,
                        audio_parameters=AudioQuality.STUDIO,
                        video_parameters=VideoQuality.HD_720P
                    )
            else:
                try:
                    from pytgcalls.types.input_stream.quality import HighQualityAudio
                    stream = AudioPiped(link, audio_parameters=HighQualityAudio())
                except:
                    from pytgcalls.types import AudioQuality
                    stream = AudioPiped(link, audio_parameters=AudioQuality.STUDIO)
        except Exception as e:
            raise AssistantErr(f"Stream Error: {e}")

        try:
            await assistant.join_group_call(
                chat_id,
                stream,
            )
        except Exception as e:
            # Handle AlreadyJoined variants in v0.9.x vs v2.x
            if "AlreadyJoined" in str(e):
                try:
                    await assistant.change_stream(chat_id, stream)
                except Exception as inner_e:
                    raise AssistantErr(f"Change Stream Error: {inner_e}")
            elif "NoActiveGroupCall" in str(e):
                raise AssistantErr("No Active Group Call Found.")
            elif "TelegramServerError" in str(e):
                raise AssistantErr("Telegram Server Error. Please try again later.")
            else:
                raise AssistantErr(f"Join Call Error: {e}")

        await add_active_chat(chat_id)
        if video:
            await add_active_video_chat(chat_id)

    async def start(self):
        LOGGER(__name__).info("Starting PyTgCalls Clients...\n")
        if config.STRING1:
            await self.one.start()
        if config.STRING2:
            await self.two.start()
        if config.STRING3:
            await self.three.start()
        if config.STRING4:
            await self.four.start()
        if config.STRING5:
            await self.five.start()

    async def decorators(self):
        clients = []
        if config.STRING1: clients.append(self.one)
        if config.STRING2: clients.append(self.two)
        if config.STRING3: clients.append(self.three)
        if config.STRING4: clients.append(self.four)
        if config.STRING5: clients.append(self.five)

        for client in clients:
            # Dynamic handler registration
            try:
                @client.on_stream_end()
                async def handler(client, update):
                    await self.change_stream(client, update.chat_id)
            except:
                pass

            try:
                @client.on_kicked()
                async def kicked_handler(client, chat_id):
                    await self.stop_stream(chat_id)
            except:
                pass

Shahil = Call()
