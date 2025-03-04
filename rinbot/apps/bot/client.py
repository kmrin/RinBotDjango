import os
import sys

from asyncio.exceptions import CancelledError
from discord import LoginFailure, Object as DiscordObj
from discord.ext.commands import Bot

from .conf import conf
from .checks import db, startup
from .log import Logger, log_exception, format_exception
from .managers import events, tasks, locale, extensions
from .helpers import generate_intents
from .tree import on_error
from .objects import TTSClient
from .utils import get_guild

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

    async def sync_commands(self) -> None:
        logger.info("Syncing commands")
        
        await self.tree.sync()
        
        if conf.testing_servers:
            logger.info("Trying to sync to provided testing guild(s)")
            
            for guild_id in conf.testing_servers:
                guild = await get_guild(self, guild_id)
                
                if guild:
                    self.tree.copy_global_to(guild=DiscordObj(guild_id))
                    await self.tree.sync(guild=guild)
                    
                    logger.info(f"Synced to guild {guild.name} ({guild_id})")
                
                else:
                    logger.warning(f"Failed to sync to guild '{guild_id}', null returned")
    
    async def setup_hook(self) -> None:
        await self.tree.set_translator(locale.Translator())
        await self.sync_commands()
    
    async def init(self) -> None:
        """
        Startup sequence
        """
        
        logger.info("Booting up")
        
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
        
        for player in list(self.music_clients.values()):
            try:
                await player.dc(force=True)
            except Exception as e:
                logger.error(f"Error disconnecting music client: {format_exception(e)}")
        
        for tts in list(self.tts_clients.values()):
            try:
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
