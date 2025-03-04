from discord import Client, Intents, LoginFailure

from ..log import Logger, log_exception


logger = Logger.STARTUP_CHECKS


async def check_token(token: str) -> bool:
    logger.info("Checking token")

    dummy = Client(intents=Intents.default())
    
    @dummy.event
    async def on_ready():
        await dummy.close()
    
    try:
        await dummy.start(token)
        
        logger.info(f"Token is valid, I am {dummy.user.display_name}!")
        return True
    
    except LoginFailure:
        await dummy.close()
        logger.error("Invalid token")
        
        return False
    
    except Exception as e:
        log_exception(e, logger, True)
        return False
