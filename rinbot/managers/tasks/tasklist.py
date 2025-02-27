import random

from discord.ext import tasks
from discord import CustomActivity
from typing import TYPE_CHECKING

from ...log import Logger
from ...conf import conf
from ..locale import get_locale

if TYPE_CHECKING:
    from ...client import Client

logger = Logger.TASKS


class TaskList:
    def __init__(self, client: "Client") -> None:
        self.client = client
    
    @tasks.loop(minutes=conf.status.interval)
    async def status_loop(self) -> None:
        if conf.debug:
            logger.debug("Status loop is in debug mode")
        
        locale = conf.status.language
        verbose = get_locale(locale)
        
        try:
            statuses = verbose.system["statuses"]
        
        except KeyError:
            logger.error(f"'statuses' key not found in '{locale}'")
            return
        
        status = random.choice(statuses)
        
        if conf.status.log:
            logger.info(f"Changing status to '{status}'")
        
        await self.client.change_presence(activity=CustomActivity(name=status))
