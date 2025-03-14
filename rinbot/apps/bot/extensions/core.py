"""
RinBot's core command cog

- Commands:
    * /ping              - Simple ping command
    * /shutdown          - Shuts down the client
    * /extensions list   - Lists the currently loaded extensions (cogs)
    * /extensions load   - Loads an extension by name
    * /extensions unload - Unloads an extension by name
    * /extensions reload - Reloads an extension by name
    * /admins me         - Attempts to add the invoker as an admin
    * /admins add        - Adds an admin
    * /admins remove     - Removes an admin
    * /owners me         - Attempts to add the invoker as an owner
    * /owners add        - Adds an owner
    * /owners remove     - Removes an owner
"""

from discord import Interaction, Embed, Member, Colour

from discord.ext.commands import (
    ExtensionNotFound,
    ExtensionNotLoaded,
    ExtensionAlreadyLoaded,
    NoEntryPointError
)

from discord.app_commands import (
    command,
    rename,
    describe,
    allowed_contexts,
    allowed_installs,
    locale_str,
    Group,
    AppCommandContext,
    AppInstallationType
)

from ..models import Admins, Owners
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


class Core(Cog, name="core"):
    def __init__(self, client: Client) -> None:
        self.client = client
    
    # Extension group
    ext_gp = Group(
        name=locale_str("core_ext_group_name"),
        description=locale_str("core_ext_group_desc"),
        allowed_contexts=AppCommandContext(guild=True, dm_channel=True, private_channel=True),
        allowed_installs=AppInstallationType(guild=True, user=True)
    )
    
    # Admins group
    admin_gp = Group(
        name=locale_str("core_admins_group_name"),
        description=locale_str("core_admins_group_desc"),
        allowed_contexts=AppCommandContext(guild=True, dm_channel=False, private_channel=True),
        allowed_installs=AppInstallationType(guild=True, user=False)
    )
    
    # Owners group
    owner_gp = Group(
        name=locale_str("core_owners_group_name"),
        description=locale_str("core_owners_group_desc"),
        allowed_contexts=AppCommandContext(guild=True, dm_channel=True, private_channel=True),
        allowed_installs=AppInstallationType(guild=True, user=True)
    )

    # /ping
    @command(
        name=locale_str("core_ping_name"),
        description=locale_str("core_ping_desc")
    )
    @allowed_contexts(True, True, True)
    @allowed_installs(True, True)
    @commands.not_blacklisted()
    async def ping(self, interaction: Interaction) -> None:
        locale = get_interaction_locale(interaction)
        message = get_localised_string(locale, "core_ping_latency", latency=round(self.client.latency * 1000))
        
        await respond(
            interaction,
            title=get_localised_string(locale, "core_ping_msg"),
            message=message
        )

    # /shutdown
    @command(
        name=locale_str("core_shutdown_name"),
        description=locale_str("core_shutdown_desc")
    )
    @allowed_contexts(True, True, True)
    @allowed_installs(True, True)
    @commands.not_blacklisted()
    @commands.is_owner()
    async def shutdown(self, interaction: Interaction) -> None:
        locale = get_interaction_locale(interaction)
        
        await respond(interaction, message=get_localised_string(locale, "core_shutdown_msg"), hidden=True)
        await self.client.stop()

    # /extensions list
    @ext_gp.command(
        name=locale_str("core_ext_list_name"),
        description=locale_str("core_ext_list_desc")
    )
    @allowed_contexts(True, True, True)
    @allowed_installs(True, True)
    @commands.not_blacklisted()
    @commands.is_owner()
    async def _ext_list(self, interaction: Interaction) -> None:
        locale = get_interaction_locale(interaction)
        
        extensions = self.client.cogs
        message = "\n".join([f"`{ext}`" for ext in extensions.keys()])
        
        embed = Embed(
            title=get_localised_string(locale, "core_ext_list_embed_title"),
            colour=Colour.gold()
        )
        
        embed.set_footer(text=get_localised_string(locale, "core_ext_list_embed_footer", count=len(extensions)))
        
        if len(extensions) > 15:
            chunks = text_to_chunks(message)
            embed.description="\n".join(chunks[0])
            view = DefaultPaginator(embed, chunks)
            
            return await respond(interaction, message=embed, view=view, hidden=True)
        
        embed.description = message
        
        await respond(interaction, message=embed, hidden=True)

    # /extensions load
    @ext_gp.command(
        name=locale_str("core_ext_load_name"),
        description=locale_str("core_ext_load_desc"),
    )
    @rename(extension=locale_str("core_ext_option_name"))
    @describe(extension=locale_str("core_ext_option_desc"))
    @allowed_contexts(True, True, True)
    @allowed_installs(True, True)
    @commands.not_blacklisted()
    @commands.is_owner()
    async def _ext_load(self, interaction: Interaction, extension: str) -> None:
        if extension.lower() in conf.internal_extensions:
            return await self.respond_with_failure(interaction, "core_ext_internal")
        
        try:
            await self.client.load_extension(f"apps.bot.extensions.{extension}")
            
            await self.respond_with_success(interaction, "core_ext_load_success", ext=extension, hidden=True)
            await self.client.sync_commands()
            
            return
        
        except ExtensionNotFound:
            key = "core_ext_not_found"
        except ExtensionAlreadyLoaded:
            key = "core_ext_already_loaded"
        except NoEntryPointError:
            key = "core_ext_no_entry"
        
        await self.respond_with_failure(interaction, key, ext=extension, hidden=True)

    # /extensions unload
    @ext_gp.command(
        name=locale_str("core_ext_unload_name"),
        description=locale_str("core_ext_unload_desc"),
    )
    @rename(extension=locale_str("core_ext_option_name"))
    @describe(extension=locale_str("core_ext_option_desc"))
    @allowed_contexts(True, True, True)
    @allowed_installs(True, True)
    @commands.not_blacklisted()
    @commands.is_owner()
    async def _ext_unload(self, interaction: Interaction, extension: str) -> None:
        # If the extension is an internal extension
        if extension.lower() in conf.internal_extensions:
            return await self.respond_with_failure(interaction, "core_ext_internal")
        
        try:
            await self.client.unload_extension(f"apps.bot.extensions.{extension}")
            
            await self.respond_with_success(interaction, "core_ext_unload_success", ext=extension, hidden=True)
            await self.client.sync_commands()
            
            return
        
        except ExtensionNotFound:
            key = "core_ext_not_found"
        except ExtensionNotLoaded:
            key = "core_ext_not_loaded"
        
        await self.respond_with_failure(interaction, key, ext=extension, hidden=True)

    # /extensions reload
    @ext_gp.command(
        name=locale_str("core_ext_reload_name"),
        description=locale_str("core_ext_reload_desc"),
    )
    @rename(extension=locale_str("core_ext_option_name"))
    @describe(extension=locale_str("core_ext_option_desc"))
    @allowed_contexts(True, True, True)
    @allowed_installs(True, True)
    @commands.not_blacklisted()
    @commands.is_owner()
    async def _ext_reload(self, interaction: Interaction, extension: str) -> None:
        # If the extension is an internal extension
        if extension.lower() in conf.internal_extensions:
            return await self.respond_with_failure(interaction, "core_ext_internal")
        
        try:
            await self.client.reload_extension(f"apps.bot.extensions.{extension}")
            
            await self.respond_with_success(interaction, "core_ext_reload_success", ext=extension, hidden=True)
            await self.client.sync_commands()
            
            return
        
        except ExtensionNotFound:
            key = "core_ext_not_found"
        except Exception as e:
            e = log_exception(e, logger)
            key = "unknown_failure"
        
        await self.respond_with_failure(interaction, key, ext=extension, hidden=True)

    # /admins me
    @admin_gp.command(
        name=locale_str("core_admins_me_name"),
        description=locale_str("core_admins_me_desc")
    )
    @allowed_contexts(True, True, True)
    @allowed_installs(True, True)
    @commands.not_blacklisted()
    async def _admins_me(self, interaction: Interaction) -> None:
        guild = interaction.guild
        user = interaction.user
        admins = await Admins.objects.filter(guild_id=guild.id, user_id=user.id).afirst()
        
        if admins:
            return await self.respond_with_failure(interaction, "core_admins_already_admin", hidden=True)
        
        if not user.guild_permissions.administrator:
            return await self.respond_with_failure(interaction, "core_admins_not_admin", hidden=True)
        
        await Admins.objects.acreate(guild_id=guild.id, user_id=user.id, user_name=user.name, guild_name=guild.name)
        
        admins = await Admins.objects.filter(guild_id=guild.id, user_id=user.id).afirst()
        
        if not admins:
            return await self.respond_with_failure(interaction, "core_admins_not_added", hidden=True)
        
        await self.respond_with_success(interaction, "core_admins_added", hidden=True)

    # /admins add
    @admin_gp.command(
        name=locale_str("core_admins_add_name"),
        description=locale_str("core_admins_add_desc")
    )
    @rename(user=locale_str("core_user_name"))
    @describe(user=locale_str("core_user_desc"))
    @allowed_contexts(True, True, True)
    @allowed_installs(True, True)
    @commands.not_blacklisted()
    @commands.is_admin()
    async def _admins_add(self, interaction: Interaction, user: Member) -> None:
        if await Admins.objects.filter(guild_id=interaction.guild.id, user_id=user.id).aexists():
            return await self.respond_with_failure(interaction, "core_admins_already_admin", hidden=True)
        
        await Admins.objects.acreate(guild_id=interaction.guild.id, user_id=user.id, user_name=user.name, guild_name=interaction.guild.name)
        
        admins = await Admins.objects.filter(guild_id=interaction.guild.id, user_id=user.id).afirst()
        
        if not admins:
            return await self.respond_with_failure(interaction, "core_admins_not_added", hidden=True)
        
        await self.respond_with_success(interaction, "core_admins_added", hidden=True)
    
    # /admins remove
    @admin_gp.command(
        name=locale_str("core_admins_remove_name"),
        description=locale_str("core_admins_remove_desc")
    )
    @rename(user=locale_str("core_user_name"))
    @describe(user=locale_str("core_user_desc"))
    @allowed_contexts(True, True, True)
    @allowed_installs(True, True)
    @commands.not_blacklisted()
    @commands.is_admin()
    async def _admins_remove(self, interaction: Interaction, user: Member) -> None:
        if not await Admins.objects.filter(guild_id=interaction.guild.id, user_id=user.id).aexists():
            return await self.respond_with_failure(interaction, "core_admins_not_admin", hidden=True)
        
        await Admins.objects.filter(guild_id=interaction.guild.id, user_id=user.id).adelete()
        
        await self.respond_with_success(interaction, "core_admins_removed", hidden=True)

    # /owners me
    @owner_gp.command(
        name=locale_str("core_owners_me_name"),
        description=locale_str("core_owners_me_desc")
    )
    @rename(token=locale_str("core_owners_me_token_name"))
    @describe(token=locale_str("core_owners_me_token_desc"))
    @allowed_contexts(True, True, True)
    @allowed_installs(True, True)
    @commands.not_blacklisted()
    async def _owners_me(self, interaction: Interaction, token: str) -> None:
        if await Owners.objects.filter(user_id=interaction.user.id).aexists():
            return await self.respond_with_failure(interaction, "core_owners_already_owner", hidden=True)
        
        if token != self.client._owner_token:
            return await self.respond_with_failure(interaction, "core_owners_invalid_token", hidden=True)
        
        await Owners.objects.acreate(
            user_id=interaction.user.id,
            user_name=interaction.user.name
        )
        
        owners = await Owners.objects.filter(user_id=interaction.user.id).afirst()
        
        if not owners:
            return await self.respond_with_failure(interaction, "core_owners_not_added", hidden=True)
        
        await self.respond_with_success(interaction, "core_owners_added", hidden=True)

    # /owners add
    @owner_gp.command(
        name=locale_str("core_owners_add_name"),
        description=locale_str("core_owners_add_desc")
    )
    @rename(user=locale_str("core_user_name"))
    @describe(user=locale_str("core_user_desc"))
    @allowed_contexts(True, True, True)
    @allowed_installs(True, True)
    @commands.not_blacklisted()
    @commands.is_owner()
    async def _owners_add(self, interaction: Interaction, user: Member) -> None:
        if await Owners.objects.filter(user_id=user.id).aexists():
            return await self.respond_with_failure(interaction, "core_owners_already_owner", hidden=True)
        
        await Owners.objects.acreate(
            user_id=user.id,
            user_name=user.name
        )
        
        owners = await Owners.objects.filter(user_id=user.id).afirst()
        
        if not owners:
            return await self.respond_with_failure(interaction, "core_owners_not_added", hidden=True)
        
        await self.respond_with_success(interaction, "core_owners_added", hidden=True)

    # /owners remove
    @owner_gp.command(
        name=locale_str("core_owners_remove_name"),
        description=locale_str("core_owners_remove_desc")
    )
    @rename(user=locale_str("core_user_name"))
    @describe(user=locale_str("core_user_desc"))
    @allowed_contexts(True, True, True)
    @allowed_installs(True, True)
    @commands.not_blacklisted()
    @commands.is_owner()
    async def _owners_remove(self, interaction: Interaction, user: Member) -> None:
        if not await Owners.objects.filter(user_id=user.id).aexists():
            return await self.respond_with_failure(interaction, "core_owners_not_owner", hidden=True)
        
        await Owners.objects.filter(user_id=user.id).adelete()
        
        await self.respond_with_success(interaction, "core_owners_removed", hidden=True)


# Setup
async def setup(client: Client) -> None:
    await client.add_cog(Core(client))
