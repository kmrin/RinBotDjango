import os
import yaml

from typing import Optional, List, Dict
from yaml import YAMLError

from ...helpers import get_os_path


def read(p: str, create: bool = False, silent: bool = False) -> Optional[List | Dict]:
    """
    Loads a YAML file from a path starting at rinbot/ and returns it

    Args:
        p (str): The path
        create (bool, optional): If the file should be created in case it doesn't exist. Defaults to False.
        silent (bool, optional): Supress any logger output. Defaults to False.

    Returns:
        Optional[List | Dict]: The read YAML data
    """

    from ...log import Logger, log_exception

    logger = Logger.YAML
    yaml_path = get_os_path(p)

    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            file = yaml.safe_load(f)

            if not silent:
                logger.info(f"Read file at: '{p}'")

            return file

    except YAMLError as e:
        if not silent:
            logger.error(f"Tried reading a file at: '{p}' but its syntax is invalid: [{e}]")

        return None

    except FileNotFoundError:
        if not silent:
            logger.error(f"Tried reading a file at: '{p}' but it doesn't exist")

        if create:
            if not silent:
                logger.warning("Creating it as per request...")

            write(p, {}, silent)

            return read(p, silent=silent)

        return None

    except Exception as e:
        log_exception(e, logger)

        return None

def write(p: str, data: List | Dict, silent: bool=False) -> bool:
    """
    Saves your data to a YAML file or creates a new one, path starts at rinbot/

    Args:
        p (str): The path
        data (List | Dict): The YAML formatted data
        silent (bool, optional): Supress any logger output. Defaults to False.

    Returns:
        bool: True if correctly writen to, otherwise False
    """

    from ...log import Logger, log_exception

    logger = Logger.YAML
    yaml_path = get_os_path(p)
    yaml_dir = os.path.dirname(yaml_path)

    os.makedirs(yaml_dir, exist_ok=True)

    try:
        with open(yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

        if not silent:
            logger.info(f"Wrote file at: '{p}'")

        file = read(p, silent=silent)

        if file == data:
            if not silent:
                logger.info("Written file validated")

            return True

        logger.error("Written file did not pass validation (missmatched data)")

        return False

    except YAMLError as e:
        if not silent:
            logger.error(f"Tried reading a file at: '{p}' but its syntax is invalid: [{e}]")

        return False

    except Exception as e:
        log_exception(e, logger)

        return False
