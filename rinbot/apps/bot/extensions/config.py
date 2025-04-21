"""
RinBot's config command cog

- Commands:
    * /configure-guild auto-role         - Automatically assign roles to new members
    * /configure-guild spam-filter       - Configure what action to take when a user is spamming
    * /configure-guild welcome-channel   - Sets a custom embed welcome message for new members
    * /configure-user translate-private  - Configure if translated messages should be private
    * /configure-user fact-check-private - Configure if fact-checked messages should be private
    * /toggle                            - Toggle a feature on or off (auto-role, spam-filter or welcome-channel)
"""

from discord import Interaction, Embed, Member, Colour, Role

from discord.ext.commands import (
    ExtensionNotFound,
    ExtensionNotLoaded,
    ExtensionAlreadyLoaded,
    NoEntryPointError,
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
    Group,
    Choice,
    AppCommandContext,
    AppInstallationType
)

from ..models import Admins, Owners, GuildConfig, Guilds, WelcomeChannels, UserConfig, AutoRole
from ..ui import DefaultPaginator
from ..checks import commands
from ..log import Logger, log_exception
from ..managers.locale import get_interaction_locale, get_localised_string
from ..responder import respond
from ..subclasses import Cog
from ..client import Client
from ..helpers import text_to_chunks
from ..conf import conf

logger = Logger.COMMANDS


class Config(Cog, name="config"):
    def __init__(self, client: Client) -> None:
        self.client = client
    
    # Configure (guild) group
    conf_gd_gp = Group(
        name=locale_str("config_conf_gd_gp_name"),
        description=locale_str("config_conf_gd_gp_desc"),
        allowed_contexts=AppCommandContext(guild=True, dm_channel=False, private_channel=False),
        allowed_installs=AppInstallationType(guild=True, user=False)
    )
    
    # Configure (user) group
    conf_us_gp = Group(
        name=locale_str("config_conf_us_gp_name"),
        description=locale_str("config_conf_us_gp_desc"),
        allowed_contexts=AppCommandContext(guild=False, dm_channel=True, private_channel=True),
        allowed_installs=AppInstallationType(guild=False, user=True)
    )
    
    # Toggle group
    toggle_gp = Group(
        name=locale_str("config_toggle_gp_name"),
        description=locale_str("config_toggle_gp_desc"),
        allowed_contexts=AppCommandContext(guild=True, dm_channel=False, private_channel=False),
        allowed_installs=AppInstallationType(guild=True, user=False)
    )
    
    # /configure-guild auto-role
    @conf_gd_gp.command(
        name=locale_str("config_conf_ar_name"),
        description=locale_str("config_conf_ar_desc")
    )
    @rename(role=locale_str("config_conf_ar_role"))
    @describe(role=locale_str("config_conf_ar_role_desc"))
    @commands.not_blacklisted()
    # @commands.is_admin()
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True)
    async def auto_role(self, interaction: Interaction, role: Role) -> None:
        _, created = await AutoRole.objects.aupdate_or_create(
            guild_id=interaction.guild.id,
            defaults={
                'guild_id': interaction.guild.id,
                'guild_name': interaction.guild.name,
                'role_id': role.id,
                'role_name': role.name
            }
        )
        
        if created:
            await self.respond_with_success(interaction, "config_conf_ar_success", role=role.name)
        else:
            await self.respond_with_success(interaction, "config_conf_ar_updated", role=role.name)

    # /configure-guild spam-filter
    @conf_gd_gp.command(
        name=locale_str("config_conf_sf_name"),
        description=locale_str("config_conf_sf_desc")
    )
    @rename(
        action=locale_str("config_conf_sf_action"),
        message=locale_str("config_conf_sf_message")
    )
    @describe(
        action=locale_str("config_conf_sf_action_desc"),
        message=locale_str("config_conf_sf_message_desc")
    )
    @choices(
        action=[
            Choice(name=locale_str("config_conf_sf_action_disabled"), value=0),
            Choice(name=locale_str("config_conf_sf_action_delete"), value=1),
            Choice(name=locale_str("config_conf_sf_action_kick"), value=2)
        ]
    )
    @commands.not_blacklisted()
    # @commands.is_admin()
    @bot_has_permissions(manage_messages=True)
    @has_permissions(manage_messages=True)
    async def spam_filter(self, interaction: Interaction, action: Choice[int], message: str) -> None:
        _, created = await GuildConfig.objects.aupdate_or_create(
            guild_id=interaction.guild.id,
            defaults={
                'guild_id': interaction.guild.id,
                'guild_name': interaction.guild.name,
                'spam_filter_action': action.value,
                'spam_filter_message': message
            }
        )
        
        if created:
            await self.respond_with_success(interaction, "config_conf_sf_success")
        else:
            await self.respond_with_success(interaction, "config_conf_sf_updated")
    

# Setup
async def setup(client: Client) -> None:
    await client.add_cog(Config(client))
