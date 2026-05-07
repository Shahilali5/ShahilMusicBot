import asyncio
import os
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError
from ShahilMusic import app, LOGGER
from ShahilMusic.misc import SUDOERS
import config

async def auto_update():
    if not config.AUTO_UPDATE:
        return
    
    while True:
        try:
            repo = Repo()
            # Fetch updates from origin
            repo.remotes.origin.fetch()
            
            # Check for new commits
            commits_behind = list(repo.iter_commits(f"HEAD..origin/{config.UPSTREAM_BRANCH}"))
            
            if commits_behind:
                LOGGER(__name__).info(f"Auto-update: {len(commits_behind)} new commits found.")
                
                # Notify SUDOERS
                for user_id in SUDOERS:
                    try:
                        await app.send_message(
                            user_id,
                            f"<b>🚀 ᴀᴜᴛᴏ ᴜᴘᴅᴀᴛᴇ ᴅᴇᴛᴇᴄᴛᴇᴅ!</b>\n\nғᴏᴜɴᴅ <b>{len(commits_behind)}</b> ɴᴇᴡ ᴄᴏᴍᴍɪᴛs ɪɴ ʀᴇᴘᴏsɪᴛᴏʀʏ.\n\n<b>➣ ᴜᴘᴅᴀᴛɪɴɢ ᴛʜᴇ ʙᴏᴛ ɴᴏᴡ...</b>"
                        )
                    except:
                        pass
                
                # Perform the update
                os.system("git stash &> /dev/null && git pull")
                os.system("pip3 install -r requirements.txt")
                
                LOGGER(__name__).info("Auto-update: Changes pulled. Restarting...")
                
                # Restart
                os.system(f"kill -9 {os.getpid()} && bash start")
                return # Task ends as process is killed
                
        except (GitCommandError, InvalidGitRepositoryError):
            LOGGER(__name__).warning("Auto-update: Git repository not found or command failed.")
        except Exception as e:
            LOGGER(__name__).error(f"Auto-update error: {e}")
            
        # Wait for 1 hour before next check
        await asyncio.sleep(3600)
