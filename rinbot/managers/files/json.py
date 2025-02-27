import os
import json

from typing import Optional, Dict, List
from json import JSONDecodeError

from ...helpers import get_os_path


def read(p: str, create: bool = False, silent: bool = False) -> Optional[List | Dict]:
    """
    Loads a JSON file from a path starting at rinbot/ and returns it

    Args:
        p (str): The path
        create (bool, optional): If the file should be created in case it doesn't exist
        silent (bool, optional): Supress any logger output

    Returns:
        Optional[List | Dict]: The read JSON data
    """

    from ...log import Logger, log_exception

    logger = Logger.JSON
    json_path = get_os_path(p)

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            file = json.load(f)

            if not silent:
                logger.info(f"Read file at: '{p}'")

            return file

    except JSONDecodeError as e:
        if not silent:
            logger.error(
                f"Tried reading a file at '{p}' but it's sintax is invalid " \
                f"[POS: {e.pos} | LINE No.: {e.lineno} | COL No.: {e.colno}]"
            )

        return None

    except FileNotFoundError:
        if not silent:
            logger.error(f"Tried reading a file at: '{p}' but it doesn't exist")

        if create:
            if not silent:
                logger.warning("Creating it as per request...")

            write(p, {}, silent)

            return read(p, silent=silent)

    except Exception as e:
        log_exception(e, logger)

        return None


def write(p: str, data: List | Dict, silent: bool=False) -> bool:
    """
    Saves your data to a JSON file or creates a new one, path starts at rinbot/

    Args:
        p (str): The path
        data (List | Dict): The JSON formatted data
        silent (bool, optional): Supress any logger output. Defaults to False.

    Returns:
        bool: True if correctly writen to, otherwise False
    """

    from ...log import Logger, log_exception

    logger = Logger.JSON
    json_path = get_os_path(p)
    json_dir = os.path.dirname(json_path)

    os.makedirs(json_dir, exist_ok=True)

    try:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        if not silent:
            logger.info(f"Wrote file at: '{p}'")

        file = read(p, silent=silent)

        if file == data:
            if not silent:
                logger.info("Written file validated")

            return True

        logger.error("Written file did not pass validation (mismatched data)")

        return False

    except JSONDecodeError as e:
        if not silent:
            logger.error(
                f"Tried reading a file at '{p}' but it's sintax is invalid " \
                f"[POS: {e.pos} | LINE No.: {e.lineno} | COL No.: {e.colno}]"
            )

        return False

    except Exception as e:
        log_exception(e, logger)

        return False
