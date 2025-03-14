from discord import (
    Interaction,
    Embed,
    Colour,
    Message,
    NotFound,
    InteractionResponded,
    HTTPException
)
from discord.ui import View
from discord.utils import MISSING
from typing import Optional, Any

from .objects import Response
from .log import Logger, log_exception

logger = Logger.RESPONDER


async def _send(
        ctx: Interaction,
        embed: Optional[Embed] = MISSING,
        view: Optional[View] = MISSING,
        outside_content: Optional[str] = None,
        hidden: bool = False,
        resp_type: Response | int = Response.SEND,
        __attempted_followup: bool = False,
        __attempted_channel: bool = False
) -> Optional[Message | Any]:
    """
    Internal function to send a response to a Discord interaction.
    
    Attempts to send a message using the specified response type, with fallbacks
    if the primary method fails.
    
    Args:
        ctx: The Discord interaction context
        embed: Optional embed to send
        view: Optional view (UI components) to send
        outside_content: Optional text content to send
        hidden: Whether the response should be ephemeral (only visible to the command user)
        resp_type: The type of response to send (SEND, FOLLOWUP, or CHANNEL)
        __attempted_followup: Internal flag to track if followup has been attempted
        __attempted_channel: Internal flag to track if channel send has been attempted
        
    Returns:
        The sent message object or None if sending failed
    """
    
    try:
        if isinstance(resp_type, Response):
            resp_type = resp_type.value
            
        if resp_type == Response.SEND.value:
            return await ctx.response.send_message(
                content=outside_content, embed=embed, view=view, ephemeral=hidden)
        elif resp_type == Response.FOLLOWUP.value:
            return await ctx.followup.send(
                content=outside_content, embed=embed, view=view, ephemeral=hidden)
        elif resp_type == Response.CHANNEL.value:
            return await ctx.channel.send(
                content=outside_content, embed=embed, view=view)

        return None

    except (NotFound, InteractionResponded):
        if not __attempted_followup:
            logger.error("Error sending response, trying to send it again using the followup method")
            return await _send(
                ctx, embed, view, outside_content, hidden, 
                Response.FOLLOWUP.value, True, False
            )
        elif not __attempted_channel:
            logger.error("Error sending response, trying to send it again using the channel method")
            return await _send(
                ctx, embed, view, outside_content, hidden,
                Response.CHANNEL.value, True, True
            )
        else:
            logger.error("Error sending response: all methods failed")
            return None

    except HTTPException as e:
        logger.error(
            f"An HTTP error occurred while trying to respond: "
            f"[HTTP CODE: {e.status} | DC CODE: {e.code} | TEXT: {e.text}]"
        )
        return None

    except AttributeError as e:
        pass

    except Exception as e:
        log_exception(e, logger)
        return None


async def respond(
        ctx: Interaction,
        colour: Colour = Colour.gold(),
        message: Optional[str | Embed] = None,
        title: Optional[str] = None,
        view: Optional[View] = None,
        outside_content: Optional[str] = None,
        hidden: bool = False,
        resp_type: Response = Response.SEND,
        silent: bool = False
) -> None:
    """
    Send a response to a Discord interaction.
    
    This function handles creating and sending embeds, views, or both to respond
    to a Discord interaction. It also logs the response details.
    
    Args:
        ctx: The Discord interaction context
        colour: The colour for the embed (if creating one)
        message: The message content or a pre-built Embed
        title: The title for the embed (if creating one)
        view: Optional view (UI components) to send
        outside_content: Optional text content to send outside the embed
        hidden: Whether the response should be ephemeral (only visible to the command user)
        resp_type: The type of response to send (SEND, FOLLOWUP, or CHANNEL)
        silent: Whether to suppress logging the response
    """
    
    if not isinstance(message, Embed):
        if message and title:
            embed = Embed(title=title, description=message, colour=colour)
        elif message:
            embed = Embed(description=message, colour=colour)
        elif title:
            embed = Embed(title=title, colour=colour)
        else:
            embed = None
    else:
        embed = message

    author = ctx.user
    guild = ctx.guild
    channel = ctx.channel
    
    await _send(
        ctx, 
        embed=embed, 
        view=view, 
        outside_content=outside_content, 
        hidden=hidden, 
        resp_type=resp_type.value
    )
    
    if silent:
        return
        
    if embed and view:
        response_type = "Embed + View"
    elif embed:
        response_type = "Embed"
    elif view:
        response_type = "View"
    else:
        response_type = "Content only"
    
    message_content = embed.description or embed.title if embed else outside_content or "[No content]"
    
    if guild:
        logger.info(
            f"Response sent: [TYPE: {response_type} | "
            f"GUILD: {guild} (ID: {guild.id}) | "
            f"AUTHOR: {author} (ID: {author.id if author else 0}) | "
            f"CH: {channel.name} (ID: {channel.id}) | "
            f"MSG: {message_content}]"
        )
    else:
        logger.info(
            f"Response sent: [TYPE: {response_type} | "
            f"AUTHOR: {author} (ID: {author.id if author else 0}) | "
            f"DMs | MSG: {message_content}]"
        )
