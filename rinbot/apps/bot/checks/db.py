from inspect import getmembers, ismethod
from typing import TYPE_CHECKING
from django.db.models import Q
from discord import TextChannel, CategoryChannel, ForumChannel

from ..utils import get_guild, get_channel, log_errors
from ..log import Logger, format_exception

from ..models import (
    AutoRole,
    Guilds,
    GuildConfig,
    Users,
    UserConfig,
    WelcomeChannels
)

if TYPE_CHECKING:
    from ..client import Client

logger = Logger.DB


class DBManager:
    def __init__(self, client: "Client") -> None:
        self.client = client

    async def check_all(self) -> None:
        logger.info("Performing all checks")
        
        for name, method in getmembers(self, ismethod):
            if name.startswith("check_") and name != "check_all":
                await method()
        
        logger.info("Finished")

    @log_errors(logger, is_async=True)
    async def check_auto_role(self) -> None:
        logger.info("Checking auto roles")
                
        async for auto_role in AutoRole.objects.all():
            guild = await get_guild(self.client, auto_role.guild_id)
            
            if not guild:
                logger.info(f"Guild {auto_role.guild_id} no longer exists or I'm not in it")
                await auto_role.adelete()
                
                continue
            
            if guild.name != auto_role.guild_name:
                auto_role.guild_name = guild.name
                await auto_role.asave(update_fields=['guild_name'])
            
            role = guild.get_role(auto_role.role_id)
            
            if not role:
                logger.info(f"Role {auto_role.role_id} no longer exists in guild {guild.name}")
                await auto_role.adelete()
                
                continue
            
            if role.name != auto_role.role_name:
                auto_role.role_name = role.name
                await auto_role.asave(update_fields=['role_name'])

    @log_errors(logger, is_async=True)
    async def check_guilds(self) -> None:
        logger.info("Checking guilds")
        
        bot_guilds = self.client.guilds
        bot_guild_ids = [guild.id for guild in bot_guilds]
        
        async for guild in Guilds.objects.all():
            if guild.guild_id not in bot_guild_ids:
                logger.info(f"Guild {guild.guild_id} no longer exists or I'm not in it")
                await guild.adelete()
                
        for guild in bot_guilds:
            _, created = await Guilds.objects.aupdate_or_create(
                guild_id=guild.id,
                defaults={
                    'guild_name': guild.name,
                    'user_count': guild.member_count
                }
            )
            
            if created:
                logger.info(f"Added missing: {guild.name} ({guild.id})")
            else:
                logger.info(f"Updated: {guild.name} ({guild.id})")

    @log_errors(logger, is_async=True)
    async def check_guild_config(self) -> None:
        logger.info("Checking guild configurations")
        
        guilds = Guilds.objects.all()
        
        async for guild in guilds:
            try:
                _, created = await GuildConfig.objects.aget_or_create(
                    guild=guild,
                    defaults={
                        'spam_filter_action': 0
                    }
                )
                
                if created:
                    logger.info(f"Added missing: {guild.guild_name} ({guild.guild_id})")
            
            except Exception as e:
                logger.error(
                    f"Error creating config for guild {guild.guild_name} ({guild.guild_id}): {format_exception(e)}"
                )
        
        orphaned_configs = GuildConfig.objects.filter(~Q(guild__in=guilds))
        count = await orphaned_configs.acount()
        
        if count > 0:
            logger.info(f"Removing {count} orphaned guild configurations.")
            await orphaned_configs.adelete()

    @log_errors(logger, is_async=True)
    async def check_users(self) -> None:
        logger.info("Checking users")
        
        bot_guilds = self.client.guilds
        db_users = Users.objects.all()
        valid_user_guilds = set()
        
        for guild in bot_guilds:
            try:
                async for member in guild.fetch_members(limit=None):
                    try:
                        valid_user_guilds.add((guild.id, member.id))
                        role_names = [role.name for role in member.roles if role.name != "@everyone"]
                        
                        _, created = await Users.objects.aupdate_or_create(
                            guild_id=guild.id,
                            user_id=member.id,
                            defaults={
                                'guild_name': guild.name,
                                'user_name': member.name,
                                'global_name': member.global_name or member.name,
                                'display_name': member.display_name,
                                'roles': role_names
                            }
                        )
                        
                        if created:
                            logger.debug(f"Added missing: {member.display_name} ({member.id}) in {guild.name}")
                    
                    except Exception as e:
                        logger.error(f"Error updating user {member.id} in guild {guild.id}: {format_exception(e)}")
            
            except Exception as e:
                logger.error(f"Error fetching members for guild {guild.name} ({guild.id}): {format_exception(e)}")
        
        async for user in db_users:
            if (user.guild_id, user.user_id) not in valid_user_guilds:
                logger.info(
                    f"User {user.display_name} ({user.user_id}) is not in {user.guild_name} ({user.guild_id}). "\
                )
                await user.adelete()

    @log_errors(logger, is_async=True)
    async def check_user_config(self) -> None:
        logger.info("Checking user configurations")
        
        users = Users.objects.all()
        
        async for user in users:
            try:
                _, created = await UserConfig.objects.aget_or_create(
                    user=user,
                    defaults={
                        'translate_private': False,
                        'fact_check_private': False
                    }
                )
                
                if created:
                    logger.debug(f"Added missing: {user.display_name} ({user.user_id}) in {user.guild_name}")
            
            except Exception as e:
                logger.error(
                    f"Error creating config for user {user.display_name} ({user.user_id}): {format_exception(e)}"
                )
        
        orphaned_configs = UserConfig.objects.filter(~Q(user__in=users))
        count = await orphaned_configs.acount()
        
        if count > 0:
            logger.info(f"Removing {count} orphaned user configurations.")
            await orphaned_configs.adelete()

    @log_errors(logger, is_async=True)
    async def check_welcome_channels(self) -> None:
        logger.info("Checking welcome channels")
            
        welcome_channels = WelcomeChannels.objects.all()
        
        async for welcome_channel in welcome_channels:
            guild = await get_guild(self.client, welcome_channel.guild_id)
            
            if not guild:
                logger.info(f"Guild {welcome_channel.guild_id} no longer exists or I'm not in it")
                await welcome_channel.adelete()
                
                continue
            
            if guild.name != welcome_channel.guild_name:
                welcome_channel.guild_name = guild.name
                await welcome_channel.asave(update_fields=['guild_name'])
            
            channel = await get_channel(self.client, welcome_channel.channel_id)
            
            if not channel:
                logger.info(
                    f"Channel {welcome_channel.channel_id} no longer exists in " \
                    f"{guild.name} (ID: {welcome_channel.guild_id})"
                )
                await welcome_channel.adelete()
                
                continue
            
            if not isinstance(channel, (TextChannel, ForumChannel, CategoryChannel)):
                logger.info(
                    f"Channel {welcome_channel.channel_id} in guild {guild.name} is not a text channel, " \
                    "forum channel, or category"
                )
                await welcome_channel.adelete()
                
                continue
            
            if channel.name != welcome_channel.channel_name:
                welcome_channel.channel_name = channel.name
                await welcome_channel.asave(update_fields=['channel_name'])
