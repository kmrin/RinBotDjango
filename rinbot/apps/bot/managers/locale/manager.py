import os

from discord import Interaction, Locale
from typing import Optional

from ...objects import Localisation
from ...log import Logger
from ...paths import Path
from ..files.yaml import read

logger = Logger.LOCALE

SECTIONS = [
    "system",
    "commands",
    "responses"
]

CHECKED: dict[str, bool] = {}
INVALID_REPORTED_KEYS: dict[str, list[str]] = {}


def check_sections(locale_file: str, locale_data: dict) -> bool:    
    for section in SECTIONS:
        if section not in locale_data:
            logger.error(f"Section '{section}' not found in locale file")
            return False
        
        if not isinstance(locale_data[section], dict):
            logger.error(f"Section '{section}' is not a dictionary")
            return False
    
    if locale_file not in CHECKED:
        logger.debug(f"Locale file at '{locale_file}' is valid")
    
    CHECKED[locale_file] = True
    
    return True


def get_locale(locale: str | Locale) -> Optional[Localisation]:
    base_locale_path = os.path.join(Path.LOCALE, f"{locale}.yml")
    
    if not os.path.exists(base_locale_path):
        logger.error(f"Locale file at '{base_locale_path}' does not exist")
        return None
    
    locale_data = read(base_locale_path, silent=True)

    if locale_data is None:
        logger.error(f"Locale file at '{base_locale_path}' is empty, invalid or doesn't exist")
        return None
    
    if not check_sections(base_locale_path, locale_data):
        logger.error(f"Locale file at '{base_locale_path}' is invalid, section check failed")
        return None
    
    return Localisation(**locale_data)


def get_interaction_locale(interaction: Interaction) -> Optional[Localisation]:
    locale = interaction.locale if interaction.locale else Locale.british_english
    
    if locale == Locale.american_english:
        locale = Locale.british_english
    
    return locale.value


def get_localised_string(locale: str, key: str, *args, **kwargs) -> Optional[str | list[str]]:
    if isinstance(locale, tuple):
        locale = locale[0]
    
    text = get_locale(locale)
    
    if not text:
        logger.error(f"Locale code '{locale}' not present in locale list, defaulting to english")
        text = get_locale("en-GB")
    
    if not text:
        logger.error("Failed to load default locale")
        return None
    
    for section in [text.system, text.commands, text.responses]:
        if key in section:
            string = section[key]
            break
    
    else:        
        if locale not in INVALID_REPORTED_KEYS:
            INVALID_REPORTED_KEYS[locale] = []
        
        if key not in INVALID_REPORTED_KEYS[locale]:
            logger.error(f"Missing localised string '{key}' for locale '{locale}'")
            INVALID_REPORTED_KEYS[locale].append(key)
        
        return None
    
    if isinstance(string, list):
        return string
    
    try:
        return string.format(*args, **kwargs)
    
    except Exception as e:
        logger.error(f"Incorrect formatting provided for string '{key}'")
        return None
