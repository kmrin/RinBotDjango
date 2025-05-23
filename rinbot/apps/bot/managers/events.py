import os
import time
import asyncio
import discord
import platform
import wavelink
import tempfile

from discord.app_commands import Command, ContextMenu
from discord import Interaction, VoiceState, Guild, Member, Message, Embed
from discord import Forbidden
from typing import TYPE_CHECKING
from gtts import gTTS

from ..helpers import hex_to_colour
from ..utils import get_full_command, get_channel, get_user_avatar
from ..conf import conf
from ..log import Logger, format_exception
from ..subclasses import Cog
from ..objects import TTSClient
from ..models import WelcomeChannels, AutoRole, GuildConfig

if TYPE_CHECKING:
    from ..client import Client

logger = Logger.EVENTS
user_message_times: dict[int, list[float]] = {}

SPAM_TIME_WINDOW = conf.spam_filter.time_window
SPAM_MAX_PER_WINDOW = conf.spam_filter.max_per_window


async def play_tts(tts_client: TTSClient, text: str) -> None:
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
        temp_audio_path = temp_file.name
        
        await asyncio.to_thread(gTTS(text=text, lang=tts_client.language).save, temp_audio_path)
        
        while tts_client.client.is_playing():
            await asyncio.sleep(0.5)
        
        tts_client.client.play(discord.FFmpegPCMAudio(temp_audio_path))
        
        while tts_client.client.is_playing():
            await asyncio.sleep(0.5)
        
        await asyncio.to_thread(os.remove, temp_audio_path)


class EventHandler(Cog, name="event_handler"):
    def __init__(self, client: "Client") -> None:
        self.client = client
    
    @Cog.listener()
    async def on_ready(self) -> None:
        logger.info(
            f"""
            ┌─────────────────────────────────────
            │ > RinBot {conf.version}
            ├─────────────────────────────────────
            │ > Logged in as: {self.client.user.name}
            │ > PyCord version: {discord.__version__}
            │ > Python ver: {platform.python_version()}
            │ > Running on: {platform.system()} {platform.release()}
            └─────────────────────────────────────
            """
        )
        
        # Connect to lavalink
        await self._connect_to_lavalink()
        
        # Update DB
        await self.client.db_manager.check_all()
        
        # Run tasks
        await self.client.task_handler.start()
        
        logger.info("RinBot is ready")

    async def _connect_to_lavalink(self, max_retries: int = 5, retry_delay: int = 1) -> None:
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Connecting to Lavalink (Attempt {attempt}/{max_retries})")
                
                node = wavelink.Node(
                    uri=f"http://{conf.lavalink.host}:{conf.lavalink.port}",
                    password=conf.lavalink.password,
                    retries=3
                )
                
                await wavelink.Pool.connect(nodes=[node], client=self.client)
                logger.info("Successfully connected to Lavalink server")
                
                return
            
            except wavelink.LavalinkException as e:
                logger.error(f"Failed to connect to Lavalink: {format_exception(e)}")
                
                if attempt < max_retries:
                    logger.info(f"Retrying...")
                    await asyncio.sleep(retry_delay)
                
                else:
                    logger.error("Maximum retries reached. Could not connect to Lavalink server.")
            
            except Exception as e:
                logger.error(f"An unexpected error occurred while connecting to Lavalink: {format_exception(e)}")
                
                if attempt < max_retries:
                    logger.info(f"Retrying...")
                    await asyncio.sleep(retry_delay)
                
                else:
                    logger.error("Maximum retries reached. Could not connect to Lavalink server.")

    @Cog.listener()
    async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload) -> None:
        logger.info(
            f"Wavelink node ready: [Node: {payload.node} | Res.: {payload.resumed} | S. ID: {payload.session_id}]"
        )

    @Cog.listener()
    async def on_guild_join(self, guild: Guild) -> None:
        logger.info(f"Joined guild '{guild.name}' (ID: {guild.id})")
        await self.client.db_manager.check_all()
    
    @Cog.listener()
    async def on_guild_remove(self, guild: Guild) -> None:
        logger.info(f"Left guild '{guild.name}' (ID: {guild.id})")
        await self.client.db_manager.check_all()

    @Cog.listener()
    async def on_member_join(self, member: Member) -> None:
        logger.info(
            f"Member {member.name} (ID: {member.id}) has joined guild {member.guild.name} (ID: {member.guild.id})"
        )
        
        await self.client.db_manager.check_all()
        
        await self._on_member_join_action_welcome(member)
        await self._on_member_join_action_role(member)

    async def _on_member_join_action_welcome(self, member: Member) -> None:
        logger.info(f"Performing welcome action for {member.display_name} (ID: {member.id})")
        
        guild = member.guild
        welcome_data = await WelcomeChannels.objects.filter(guild_id=guild.id).afirst()
        
        if not welcome_data:
            logger.info(f"No welcome channel setting found for {guild.name} (ID: {guild.id})")
            return
        
        if not welcome_data.active or not welcome_data.channel_id:
            logger.info(
                f"Welcome channel setting is not active or channel ID is not set for {guild.name} (ID: {guild.id})"
            )
            return
        
        channel = await get_channel(self.client, welcome_data.channel_id)
        
        if not channel:
            logger.error(f"Channel with ID {welcome_data.channel_id} not found in {guild.name} (ID: {guild.id})")
            return
        
        title = welcome_data.title
        description = welcome_data.description
        
        if "<username>" in title:
            title = title.replace("<username>", member.display_name)
        
        embed = Embed(
            title=title,
            colour=hex_to_colour(welcome_data.colour)
        )
        
        if description:
            if "<username>" in description:
                description = description.replace("<username>", member.display_name)
            elif "<mention>" in description:
                description = description.replace("<mention>", member.mention)
            
            embed.description = description
        
        user_pic = await get_user_avatar(member)
        
        if welcome_data.show_pfp == 1:
            embed.set_thumbnail(url=user_pic)
        
        elif welcome_data.show_pfp == 2:
            embed.set_image(url=user_pic)
        
        await channel.send(embed=embed)

    async def _on_member_join_action_role(self, member: Member) -> None:
        logger.info(f"Performing auto-role action for {member.display_name} (ID: {member.id})")
        
        guild = member.guild
        me = guild.me
        
        auto_roles = await AutoRole.objects.filter(guild_id=guild.id).afirst()
        
        if not auto_roles:
            logger.info(f"No auto-role setting found for {guild.name} (ID: {guild.id})")
            return
        
        if not auto_roles.active or not auto_roles.role_id:
            logger.info(f"Auto-role setting is not active or role ID is not set for {guild.name} (ID: {guild.id})")
            return
        
        role = await guild.fetch_role(auto_roles.role_id)
        
        if not role:
            logger.error(f"Role with ID {auto_roles.role_id} not found in {guild.name} (ID: {guild.id})")
            return
        
        if role in member.roles:
            logger.info(f"Role '{role.name}' is already assigned to {member.display_name} (ID: {member.id})")
            return
        
        logger.info(f"Adding role '{role.name}' to {member.display_name} (ID: {member.id})")
        
        if not me.guild_permissions.manage_roles:
            logger.warning(f"I do not have permission to manage roles in {guild.name} (ID: {guild.id})")
            return
        
        try:
            await member.add_roles(role)
        
        except Forbidden:
            logger.warning(
                f"I am unable to assign '{role.name}' to {member.display_name} (ID: {member.id}), " \
                "role is probably higher than my highest role"
            )

    @Cog.listener()
    async def on_member_remove(self, member: Member) -> None:
        logger.info(
            f"Member {member.name} (ID: {member.id}) has left guild {member.guild.name} (ID: {member.guild.id})"
        )

    async def _on_spam_action(self, message: Message) -> None:
        logger.warning(
            f"Spam detected from {message.author.display_name} (ID: {message.author.id}) " \
            f"in {message.guild.name} (ID: {message.guild.id})"
        )
        
        me = message.guild.me
        guild_config = await GuildConfig.objects.filter(guild_id=message.guild.id).afirst()
        
        if not guild_config:
            logger.info(f"No spam filter setting found for {message.guild.name} (ID: {message.guild.id})")
            return
        
        if guild_config.spam_filter_action == 0:
            logger.info(f"Spam filter is disabled for {message.guild.name} (ID: {message.guild.id})")
            return
        
        if guild_config.spam_filter_action == 1:
            logger.info(
                f"Spam filter action is set to delete messages for {message.guild.name} (ID: {message.guild.id})"
            )
            
            if me.guild_permissions.manage_messages:
                logger.info(f"Deleting message from {message.author.display_name} (ID: {message.author.id})")
                await message.delete()
            
            spam_filter_message = guild_config.spam_filter_message
            
            if spam_filter_message:
                if "<username>" in spam_filter_message:
                    spam_filter_message = spam_filter_message.replace("<username>", message.author.display_name)
                elif "<mention>" in spam_filter_message:
                    spam_filter_message = spam_filter_message.replace("<mention>", message.author.mention)
            
                await message.channel.send(spam_filter_message)
        
        elif guild_config.spam_filter_action == 2:
            logger.info(
                f"Spam filter action is set to kick members for {message.guild.name} (ID: {message.guild.id})"
            )
            
            if me.guild_permissions.manage_messages:
                await message.delete()
            
            if me.guild_permissions.kick_members:
                logger.info(f"Kicking {message.author.display_name} (ID: {message.author.id}) for spam")
                await message.author.kick(reason="Spam")
    
    async def _on_message_tts(self, message: Message) -> None:
        if (
            message.guild.id in self.client.tts_clients.keys()
            and message.content and len(message.content) <= 250
        ):
            tts_client = self.client.tts_clients[message.guild.id]
            msg = f"{message.author.name}: {message.content}" if tts_client.blame else message.content
            
            await play_tts(tts_client, msg)
    
    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.author.bot or message.author.system or message.author == self.client.user:
            return
        
        if not message.guild:
            return
        
        if conf.debug and message.content:
            logger.debug(
                f"Message '{message.content}' sent by {message.author.display_name} " \
                f"in {message.channel} at {message.guild}"
            )
        
        # Anti-spam
        if conf.spam_filter.enabled:
            user_id = message.author.id
            current_time = time.time()
            
            if user_id not in user_message_times:
                user_message_times[user_id] = []
            
            user_message_times[user_id].append(current_time)
            
            user_message_times[user_id] = [
                t for t in user_message_times[user_id] 
                if current_time - t <= SPAM_TIME_WINDOW
            ]
            
            if len(user_message_times[user_id]) > SPAM_MAX_PER_WINDOW:
                return await self._on_spam_action(message)
        
        await self._on_message_tts(message)

    @Cog.listener()
    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState) -> None:
        if (member.id != self.client.user.id) or (before.channel is None):
            return
        
        if after.channel:
            for member in after.channel.members:
                if member.id == self.client.user.id:
                    return
        
        guild = before.channel.guild
        
        logger.warning(f"Disconnected from '{before.channel.name}' in '{guild.name}' (ID: {guild.id})")
        
        if guild.id in self.client.tts_clients.keys():
            del self.client.tts_clients[guild.id]
            logger.info(f"Closed a TTS client that was active there")
        
        elif guild.id in self.client.music_clients.keys():
            del self.client.music_clients[guild.id]
            logger.info(f"Closed a music client that was active there")

    @Cog.listener()
    async def on_app_command_completion(self, interaction: Interaction, command: Command | ContextMenu) -> None:
        guild = interaction.guild.name if interaction.guild else "DMs"
        guild_id = interaction.guild.id if interaction.guild else None
        user = interaction.user.name
        user_id = interaction.user.id
        
        command_name = get_full_command(interaction)
        
        logger.info(
            f"Command '{command_name}' executed by {user} (ID: {user_id}) in {guild} (ID: {guild_id})"
        )
