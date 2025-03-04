import os
import asyncio
import threading
import sys
import atexit

from django.apps import AppConfig


class BotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.bot'
    verbose_name = 'Rinbot Discord Bot'
    bot_thread = None
    client = None
    
    def ready(self):
        if 'runserver' not in sys.argv and 'gunicorn' not in sys.argv[0]:
            return
            
        if threading.current_thread() is not threading.main_thread():
            return
            
        if os.getenv('BOT_RUN_WITH_DJANGO', 'False') == 'True':
            from .client import Client
            
            if BotConfig.bot_thread is not None and BotConfig.bot_thread.is_alive():
                return
                
            def run_bot():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                BotConfig.client = Client()
                loop.run_until_complete(BotConfig.client.init())
            
            def shutdown_bot():
                if BotConfig.client:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(BotConfig.client.stop())
                    loop.close()
            
            atexit.register(shutdown_bot)
            
            BotConfig.bot_thread = threading.Thread(target=run_bot)
            BotConfig.bot_thread.start()
