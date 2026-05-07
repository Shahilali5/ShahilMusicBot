from ShahilMusic.core.bot import Shahil
from ShahilMusic.core.dir import dirr
from ShahilMusic.core.git import git
from ShahilMusic.core.userbot import Userbot
from ShahilMusic.misc import dbb, heroku

from .logging import LOGGER


def _patch_pytgcalls_update_group_call() -> None:
	try:
		from pyrogram.raw.types import UpdateGroupCall
	except Exception:
		return

	if hasattr(UpdateGroupCall, "chat_id"):
		return

	def _chat_id(self):
		peer = getattr(self, "peer", None)
		if peer is None:
			return None
		if hasattr(peer, "user_id"):
			return peer.user_id
		if hasattr(peer, "channel_id"):
			return -1000000000000 - peer.channel_id
		if hasattr(peer, "chat_id"):
			return -peer.chat_id
		return None

	UpdateGroupCall.chat_id = property(_chat_id)

dirr()
git()
dbb()
heroku()
_patch_pytgcalls_update_group_call()

app = Shahil()
userbot = Userbot()


from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()
