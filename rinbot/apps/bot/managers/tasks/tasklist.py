import random
import datetime

from discord.ext import tasks
from discord import CustomActivity, Embed, Colour
from typing import TYPE_CHECKING
from django.utils.timezone import now

from ...log import Logger
from ...conf import conf
from ...utils import get_user
from ..locale import get_locale, get_localised_string
from ...models import Birthdays

if TYPE_CHECKING:
    from ...client import Client

logger = Logger.TASKS


class TaskList:
    def __init__(self, client: "Client") -> None:
        self.client = client
    
    @tasks.loop(minutes=conf.status.interval)
    async def status_loop(self) -> None:
        locale = conf.status.language
        verbose = get_locale(locale)
        
        if conf.debug:
            status = verbose.system["maintenance_status"]
            return await self.client.change_presence(activity=CustomActivity(name=status))
        
        try:
            statuses = verbose.system["statuses"]
        
        except KeyError:
            logger.error(f"'statuses' key not found in '{locale}'")
            return
        
        status = random.choice(statuses)
        
        if conf.status.log:
            logger.info(f"Changing status to '{status}'")
        
        await self.client.change_presence(activity=CustomActivity(name=status))
    
    @tasks.loop(time=datetime.time(hour=0, minute=0))
    async def birthday_check(self) -> None:
        today = now().date()
        today_month_day = (today.month, today.day)
        birthdays = Birthdays.objects.all()
        
        for birthday in birthdays:
            birthday_date = birthday.date
            if (birthday_date.month, birthday_date.day) == today_month_day:
                user = await get_user(self.client, birthday.user_id)
                
                if user:
                    try:
                        locale = birthday.user_locale
                        title = get_localised_string(locale, "birthday_title")
                        description = get_localised_string(locale, "birthday_description", name=birthday.name)
                        
                        if not title or not description:
                            logger.error(f"Failed to get localised birthday strings for locale '{locale}'")
                            continue
                        
                        embed = Embed(
                            title=title,
                            description=description,
                            colour=Colour.gold()
                        )
                        
                        await user.send(embed=embed)
                        logger.info(f"Sent birthday message to {user.name} (ID: {user.id})")
                    
                    except Exception as e:
                        logger.error(f"Failed to send birthday message to user {birthday.user_id}: {e}")
                
                else:
                    logger.warning(f"Could not find user with ID {birthday.user_id} for birthday notification")
