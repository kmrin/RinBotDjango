from discord import Interaction
from discord.app_commands import check
from typing import Callable, TypeVar

from ..log import Logger
from ..errors import UserBlacklisted, UserNotAdmin, UserNotInGuild, UserNotOwner
from ..utils import get_member
from ..models import Owners, Blacklist

logger = Logger.COMMAND_CHECKS

T = TypeVar("T")


def is_guild() -> Callable[[T], T]:
    async def predicate(interaction: Interaction) -> bool:
        if not interaction.guild:
            raise UserNotInGuild(interaction)
        
        return True
    
    return check(predicate)


def is_owner() -> Callable[[T], T]:
    async def predicate(interaction: Interaction) -> bool:
        if not await Owners.objects.filter(user_id=interaction.user.id).aexists():
            raise UserNotOwner(interaction)
        
        return True
    
    return check(predicate)


def is_admin() -> Callable[[T], T]:
    async def predicate(interaction: Interaction) -> bool:
        if not interaction.guild:
            raise UserNotInGuild(interaction)
        
        member = await get_member(interaction.client, interaction.guild, interaction.user.id)
        
        if not member:
            logger.warning(f"Couldn't fetch member for user '{interaction.user.id}'")
            raise UserNotAdmin(interaction)
        
        if not member.guild_permissions.administrator:
            raise UserNotAdmin(interaction)
        
        return True
    
    return check(predicate)


def not_blacklisted() -> Callable[[T], T]:
    async def predicate(interaction: Interaction) -> bool:
        if await Blacklist.objects.filter(user_id=interaction.user.id).aexists():
            raise UserBlacklisted(interaction)
        
        return True
    
    return check(predicate)
