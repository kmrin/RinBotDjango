from discord import Interaction, Colour
from discord.app_commands import MissingPermissions, BotMissingPermissions
from discord.app_commands.errors import AppCommandError, TransformerError

from .managers.locale import get_interaction_locale, get_localised_string
from .log import Logger, log_exception
from .responder import respond

logger = Logger.TREE


async def on_error(interaction: Interaction, error: AppCommandError) -> None:
    locale = get_interaction_locale(interaction)
    
    if isinstance(error, MissingPermissions):
        key = "tree_missing_perms"
        perms = ", ".join(error.missing_permissions)
        
        string = get_localised_string(locale, key, perms=perms) if perms else get_localised_string(locale, key)
        await respond(interaction, Colour.red(), string, hidden=True)

    elif isinstance(error, BotMissingPermissions):
        key = "tree_bot_missing_perms"
        perms = ", ".join(error.missing_permissions)
        
        string = get_localised_string(locale, key, perms=perms) if perms else get_localised_string(locale, key)
        await respond(interaction, Colour.red(), string, hidden=True)
    
    elif isinstance(error, TransformerError):
        key = "tree_transformer_error"
        
        logger.warning(
            f"Transformer failure: [Converting: {error.value} | To: {error.transformer._error_display_name!s}]"
        )
        
        string = get_localised_string(locale, key)
        await respond(interaction, Colour.red(), string, hidden=True)
    
    else:
        try:
            raise error
        except Exception as e:
            log_exception(e, logger)
