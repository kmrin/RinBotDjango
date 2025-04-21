import os
import asyncio
import threading
import sys
import atexit
import signal

from django.apps import AppConfig
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import Client


class BotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.bot'
    verbose_name = 'Rinbot Discord Bot'
    bot_thread: threading.Thread | None = None
    bot_loop: asyncio.AbstractEventLoop | None = None
    client: Client | None = None
    
    def ready(self):
        if 'runserver' not in sys.argv and 'gunicorn' not in sys.argv[0]:
            return
            
        if threading.current_thread() is not threading.main_thread():
            return
            
        if os.getenv('BOT_RUN_WITH_DJANGO', 'False') == 'True':
            from .client import Client
            from .log import Logger
            
            logger = Logger.CLIENT
            
            if BotConfig.bot_thread is not None and BotConfig.bot_thread.is_alive():
                return
                
            def run_bot():
                BotConfig.bot_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(BotConfig.bot_loop)
                
                BotConfig.client = Client()
                BotConfig.bot_loop.run_until_complete(BotConfig.client.init())
            
            def shutdown_bot(*args, **kwargs):
                logger.info("Received shutdown signal!")
                if BotConfig.client and BotConfig.bot_loop:
                    try:
                        future = asyncio.run_coroutine_threadsafe(
                            BotConfig.client.stop(), 
                            BotConfig.bot_loop
                        )
                        
                        future.result(timeout=10)
                        logger.info("Bye!")
                    
                    except Exception as _:
                        # TODO: Figure out the unknown error happening during shutdown, but for now it seems harmless
                        pass
                        
                    finally:
                        if BotConfig.bot_loop and BotConfig.bot_loop.is_running():
                            BotConfig.bot_loop.stop()
            
            atexit.register(shutdown_bot)
            
            for sig in [signal.SIGINT, signal.SIGTERM]:
                signal.signal(sig, shutdown_bot)
            
            BotConfig.bot_thread = threading.Thread(target=run_bot, daemon=True)
            BotConfig.bot_thread.start()
