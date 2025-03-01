import os

from typing import TYPE_CHECKING

from ..log import Logger, format_exception
from ..paths import Path
from ..conf import conf

if TYPE_CHECKING:
    from ..client import Client

logger = Logger.LOADER


async def load_extensions(client: "Client") -> None:
    nsfw_extensions = {
        "danbooru": conf.nsfw_extensions.danbooru,
        "rule34": conf.nsfw_extensions.rule34,
        "e621": conf.nsfw_extensions.e621
    }
    
    for file in os.listdir(Path.EXTENSIONS):
        if file.endswith(".py"):
            extension = file[:-3]
            
            if extension in nsfw_extensions:
                ext_config = nsfw_extensions[extension]
                
                if not ext_config.enabled or ext_config.api_key is None:
                    logger.info(f"Skipping NSFW extension '{extension}' (disabled or missing API key)")
                    continue
            
            try:
                client.load_extension(f"rinbot.extensions.{extension}")
                logger.info(f"Loaded extension: {extension}")
            
            except Exception as e:
                logger.error(f"Failed to load extension: {extension} | {format_exception(e)}")
