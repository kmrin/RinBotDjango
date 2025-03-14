import os

from discord import Locale
from typing import Optional

from discord.app_commands import (
    locale_str,
    Translator as DiscordTranslator,
    TranslationContextTypes
)

from .manager import get_localised_string
from ...paths import Path

SUPPORTED_LOCALES = os.listdir(Path.LOCALE)


class Translator(DiscordTranslator):
    async def translate(
            self,
            string: locale_str | str,
            locale: Locale,
            context: TranslationContextTypes
    ) -> Optional[str]:
        msg = string.message if string.message else string
        
        if (locale == Locale.american_english) or (locale.value not in SUPPORTED_LOCALES):
            locale = Locale.british_english
        
        localised = get_localised_string(locale.value, msg)
        
        return localised if localised else None
