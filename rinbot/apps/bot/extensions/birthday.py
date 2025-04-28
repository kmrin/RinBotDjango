"""
RinBot's birthday command cog

- Commands:
    * /birthday add    - Add a birthday
    * /birthday remove - Remove a birthday
"""

from typing import Optional
from datetime import datetime
from discord import Interaction, Embed, Role, TextChannel

from discord.ext.commands import (
    has_permissions,
    bot_has_permissions
)

from discord.app_commands import (
    command,
    rename,
    describe,
    choices,
    allowed_contexts,
    allowed_installs,
    locale_str,
    Range,
    Group,
    Choice,
    AppCommandContext,
    AppInstallationType,
)

from ..models import Birthdays
from ..checks import commands
from ..log import Logger
from ..managers.locale import get_interaction_locale, get_localised_string
from ..responder import respond
from ..subclasses import Cog
from ..client import Client
from ..helpers import is_hex_colour, hex_to_colour, bool_choice
from ..utils import get_user_avatar
from ..objects import Response, CommandOptions
from ..ui import BirthdayRemove

logger = Logger.COMMANDS


class Birthday(Cog, name="birthday"):
    def __init__(self, client: Client) -> None:
        self.client = client
    
    birthday_gp = Group(
        name=locale_str("birthday_gp_name"),
        description=locale_str("birthday_gp_desc"),
        allowed_contexts=AppCommandContext(guild=True, dm_channel=True, private_channel=True),
        allowed_installs=AppInstallationType(guild=True, user=True)
    )
    
    @birthday_gp.command(
        name=locale_str("birthday_add_name"),
        description=locale_str("birthday_add_desc")
    )
    @rename(
        day=locale_str("birthday_add_day_name"),
        month=locale_str("birthday_add_month_name"),
        name=locale_str("birthday_add_name_name")
    )
    @describe(
        day=locale_str("birthday_add_day_desc"),
        month=locale_str("birthday_add_month_desc"),
        name=locale_str("birthday_add_name_desc")
    )
    async def add(self, interaction: Interaction, day: Range[int, 1, 31], month: Range[int, 1, 12], name: str) -> None:
        birthday_obj = await Birthdays.objects.acreate(
            day=day,
            month=month,
            name=name,
            user_id=interaction.user.id,
            user_name=interaction.user.name,
            user_locale=get_interaction_locale(interaction)
        )
        await birthday_obj.asave()
        
        return await self.respond_with_success(
            interaction, "birthday_added",
            hidden=True,
            name=name,
            day=day,
            month=month
        )
    
    @birthday_gp.command(
        name=locale_str("birthday_remove_name"),
        description=locale_str("birthday_remove_desc")
    )
    async def remove(self, interaction: Interaction) -> None:
        birthdays = await Birthdays.objects.filter(user_id=interaction.user.id).acount()
        
        if birthdays == 0:
            return await self.respond_with_failure(interaction, "birthday_remove_no_birthdays")
        
        view_payload = {}
        
        async for birthday in Birthdays.objects.filter(user_id=interaction.user.id).all():
            view_payload[f"{birthday.day}/{birthday.month}"] = birthday.name
            
        logger.debug(f"Birthdays: {birthdays}")
        logger.debug(f"View payload: {view_payload}")
        
        view = BirthdayRemove(interaction, view_payload)
        await interaction.response.send_message(view=view)
        
        timeout = await view.wait()
        
        if timeout:
            return
        
        await Birthdays.objects.filter(user_id=interaction.user.id, name__in=view.selected_names).adelete()

# Setup
async def setup(client: Client) -> None:
    await client.add_cog(Birthday(client))
