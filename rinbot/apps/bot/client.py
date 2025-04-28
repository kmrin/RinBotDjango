import os
import sys

from asyncio.exceptions import CancelledError
from discord import LoginFailure
from discord.ext.commands import Bot
from secrets import token_urlsafe

from .conf import conf
from .checks import db, startup
from .log import Logger, log_exception, format_exception, BOLD, RESET
from .managers import events, tasks, locale, extensions
from .helpers import generate_intents
from .tree import TreeSync,on_error
from .objects import TTSClient

logger = Logger.CLIENT


class Client(Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix="-",
            intents=generate_intents(conf.intents),
            help_command=None
        )

        self.tree.on_error = on_error
        self.tts_clients: dict[int, TTSClient] = {}
        self.music_clients: dict[int, object] = {}  # TODO: Add music client type
        self.task_handler = tasks.TaskManager(self)
        self.db_manager = db.DBManager(self)
        self.sync_mgr = TreeSync(self)
        self._owner_token = None
    
    async def setup_hook(self) -> None:
        await self.tree.set_translator(locale.Translator())
        await self.sync_mgr.sync()
    
    async def init(self) -> None:
        """
        Startup sequence
        """
        
        self._owner_token = token_urlsafe(32)
        
        logger.info("Booting up")
        logger.info(f"{BOLD}Token for owner registration:{RESET} {self._owner_token}")
        
        await self.add_cog(events.EventHandler(self))
        logger.info("Loaded internal extensions")
        
        await extensions.load_extensions(self)
        
        try:
            if not await startup.check_token(os.getenv('BOT_DISCORD_TOKEN')):
                sys.exit(1)
            
            await self.start(os.getenv('BOT_DISCORD_TOKEN'))
        
        except LoginFailure:
            logger.critical("Could not log in to Discord, invalid token?")
            sys.exit(1)
        
        except RuntimeError:
            logger.critical("Runtime error occurred, most likely due to misconfiguration")
            sys.exit(1)
        
        except (
                KeyboardInterrupt,
                SystemExit,
                InterruptedError
        ):
            logger.warning("Interrupt detected")
            await self.close()
        
        except Exception as e:
            logger.critical(f"Fatal unexpected error occurred: {format_exception(e)}")
            log_exception(e)
            sys.exit(1)

    async def stop(self) -> None:
        """
        Shutdown sequence
        """
        
        logger.info("Shutting down bot...")
        
        self._is_closing = True
        
        for player in list(self.music_clients.values()):
            try:
                logger.info(f"Disconnecting music client in guild {player.guild.id}")
                await player.dc(force=True)
            except Exception as e:
                logger.error(f"Error disconnecting music client: {format_exception(e)}")
        
        for guild_id, tts in list(self.tts_clients.items()):
            try:
                logger.info(f"Disconnecting TTS client in guild {guild_id}")
                await tts.client.disconnect(force=True)
            except Exception as e:
                logger.error(f"Error disconnecting TTS client: {format_exception(e)}")
        
        try:
            if hasattr(self, 'task_handler'):
                await self.task_handler.cancel_all_tasks()
        except Exception as e:
            logger.error(f"Error cancelling tasks: {format_exception(e)}")
        
        try:
            await self.close()
        except CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error during bot.close(): {format_exception(e)}")
        
        logger.info("Bot has been stopped")
