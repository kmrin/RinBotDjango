import asyncio

from discord import Interaction, Embed, Colour, DMChannel
from discord.app_commands import CheckFailure
from discord.ext.commands import Context

from .managers.locale import get_interaction_locale, get_localised_string
from .log import Logger
from .utils import get_full_command
from .responder import respond

logger = Logger.ERRORS


class RinBotError:
    ...


class InteractionTimedOut(Exception):
    def __init__(self, interaction: Context | Interaction) -> None:
        asyncio.create_task(self.__do_action(interaction))

    def __str__(self) -> str:
        return "An interaction timed out"

    @staticmethod
    async def __do_action(interaction: Context | Interaction) -> None:
        locale = get_interaction_locale(interaction)
        msg = get_localised_string(locale, "error_interaction_timeout")
        embed = Embed(description=msg, colour=Colour.yellow())

        await interaction.edit_original_response(content=None, embed=embed, view=None)


class UserNotOwner(RinBotError, CheckFailure):
    def __init__(self, interaction: Interaction, empty: bool = False) -> None:
        asyncio.create_task(self.__do_action(interaction, empty))
    
    @staticmethod
    async def __do_action(interaction: Interaction, empty: bool) -> None:
        author = interaction.user
        guild = interaction.guild if interaction.guild else None
        channel = interaction.channel if interaction.channel else None
        command = get_full_command(interaction)
        
        channel = "DMs" if isinstance(interaction.channel, DMChannel) else channel.name
        
        logger.warning(
            f"Someone tried running a command of class 'owner' but they're not in this class: " \
            f"[Command: {command} | Who: {author.name} | Where: {guild.name if guild else 'DMs'}" \
            f"(ID: {guild.id if guild else author.id}) | In channel: {channel}]"
        )
        
        locale = get_interaction_locale(interaction)
        msg = get_localised_string(locale, "error_not_owner")
        empty_msg = get_localised_string(locale, "error_owners_empty")
        
        await respond(interaction, Colour.red(), msg, hidden=True)
        
        if empty:
            await respond(interaction, Colour.red(), empty_msg, hidden=True)


class UserNotAdmin(RinBotError, CheckFailure):
    def __init__(self, interaction: Interaction) -> None:
        asyncio.create_task(self.__do_action(interaction))

    @staticmethod
    async def __do_action(interaction: Interaction) -> None:
        author = interaction.user
        guild = interaction.guild if interaction.guild else None
        channel = interaction.channel or None
        command = get_full_command(interaction)
        
        logger.warning(
            f"Someone tried running a command of class 'admin' but they're not in this class: " \
            f"[Command: {command} | Who: {author.name} | Where: {guild.name if guild else 'DMs'}" \
            f"(ID: {guild.id if guild else author.id}) | In channel: {channel.name if channel else ''}]"
        )
        
        locale = get_interaction_locale(interaction)
        msg = get_localised_string(locale, "error_not_admin")
        
        await respond(interaction, Colour.red(), msg, hidden=True)


class UserBlacklisted(RinBotError, CheckFailure):
    def __init__(self, interaction: Interaction) -> None:
        asyncio.create_task(self.__do_action(interaction))

    @staticmethod
    async def __do_action(interaction: Interaction) -> None:
        author = interaction.user
        guild = interaction.guild if interaction.guild else None
        channel = interaction.channel or None
        command = get_full_command(interaction)
        
        logger.warning(
            f"Someone tried running a command but they're blacklisted:" \
            f"[Command: {command} | Who: {author.name} | Where: {guild.name if guild else 'DMs'}" \
            f"(ID: {guild.id if guild else author.id}) | In channel: {channel.name if channel else ''}]"
        )
        
        locale = get_interaction_locale(interaction)
        msg = get_localised_string(locale, "error_blacklisted")
        
        await respond(interaction, Colour.red(), msg, hidden=True)


class UserNotInGuild(RinBotError, CheckFailure):
    def __init__(self, interaction: Interaction | Context) -> None:
        asyncio.create_task(self.__do_action(interaction))
    
    @staticmethod
    async def __do_action(interaction: Interaction | Context) -> None:
        author = interaction.author if isinstance(interaction, Context) else interaction.user
        command = get_full_command(interaction) if isinstance(interaction, Interaction) else interaction.command

        logger.warning(
            f"Someone tried running a guild command in my DMs:" \
            f"[Command: {command} | Who: {author.name if author else ''} (ID: {author.id if author else 0})]"
        )
        
        locale = get_interaction_locale(interaction)
        msg = get_localised_string(locale, "error_not_in_guild")
        
        await respond(interaction, Colour.red(), msg, hidden=True)
