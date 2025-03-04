import re
import os
import string
import random

from typing import Literal, Optional
from discord import Colour, Intents
from discord.app_commands import Choice
from translate import Translator
from langdetect import detect


# Checkers
def is_hex_colour(colour: str) -> bool:
    """
    Check if a string is a valid hex colour
    """
    
    return bool(re.match(r"^#(?:[0-9a-fA-F]{6})$", colour))


# Converters
def bool_choice(choice: Literal[0, 1] | Choice) -> bool:
    """
    Convert a bool or a Choice to a bool
    """

    if isinstance(choice, Choice):
        return choice.value == 1
    return bool(choice)


def ms_to_string(ms: int) -> str:
    """
    Convert a number of milliseconds to a string
    """
    
    s = ms / 1000
    m = s / 60
    h = m / 60
    
    return (
        f"{h:02d}:{m:02d}:{s:02d}"
        if h > 0 else
        f"{m:02d}:{s:02d}"
    )


def list_to_chunks(lst: list, size: int) -> list[list]:
    """
    Splits a list into chunks of a given size
    """
    
    return [lst[i:i+size] for i in range(0, len(lst), size)]


def text_to_chunks(text: str, size: int, include_nl: bool = False) -> list[str]:
    """
    Splits a string into chunks of a given size
    """
    
    lines = text.split("\n")
    chunks = [lines[i:i+size] for i in range(0, len(lines), size)]

    if include_nl:
        return chunks

    return [
        "\n".join(chunk)
        for chunk in chunks
    ]


def hex_to_colour(hex: str) -> Colour:
    """
    Convert a hex colour to a Colour
    """
    
    return Colour.from_str(hex)


# Formatters
def remove_nl_from_string_list(lst: list[str]) -> list[str]:
    """
    Removes newlines from a list of strings
    """
    
    return [x.strip() for x in lst]


def translate(text: str, to_lang: str, from_lang: Optional[str] = None) -> str:
    """
    Translates a string from one language to another

    Args:
        text (str): The text to be translated
        to_lang (str): The output language
        from_lang (Optional[str], optional): The input language. Will try to auto-detect if not given. Defaults to None.

    Returns:
        str: The translated string
    """
    
    if not from_lang:
        from_lang = detect(text)
    
    translator = Translator(to_lang, from_lang)
    
    return translator.translate(text)


def generate_intents(intents_config: dict[str, bool]) -> Intents:
    """
    Generates an Intents object based on a dictionary of intents
    """
    
    intents = Intents.default()
    
    for intent, enabled in intents_config.items():
        setattr(intents, intent, enabled)
    
    return intents


# Getters
def get_os_path(path: str, from_root: bool = False) -> str:
    """
    Returns the real path of a given path by resolving it to the root
    """
    
    if from_root:
        return os.path.realpath(path)
    
    return os.path.realpath(os.path.join(os.path.dirname(__file__), path))


def get_random_string(length: int) -> str:
    """
    Generates a random string of a given length
    """
    
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))
