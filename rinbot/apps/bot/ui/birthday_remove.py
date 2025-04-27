from discord import Interaction, Embed, Colour, SelectOption
from discord.ui import View, Select
from typing import Dict, List

from ..managers.locale import get_interaction_locale, get_localised_string
from ..errors import InteractionTimedOut


class BirthdayRemove(View):
    def __init__(self, original_interaction: Interaction, birthday_dict: Dict[str, str]) -> None:
        super().__init__(timeout=60.0)
        
        self.original_interaction = original_interaction
        locale = get_interaction_locale(self.original_interaction)
        
        self.selected_names: List[str] = []
        self.has_options = False
        
        options = []
        for name, date in birthday_dict.items():
            options.append(
                SelectOption(
                    label=name,
                    description=date,
                    value=name
                )
            )
        
        if options:
            self.add_item(BirthdaySelect(options, locale))
            self.has_options = True
    
    async def on_timeout(self) -> None:
        self.stop()
        raise InteractionTimedOut(self.original_interaction)


class BirthdaySelect(Select):
    def __init__(self, options: List[SelectOption], locale: str) -> None:
        self.locale = locale
        
        super().__init__(
            placeholder=get_localised_string(self.locale, "ui_birthday_remove_placeholder"),
            min_values=1,
            max_values=len(options),
            options=options
        )
    
    async def callback(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        
        self.view.selected_names = self.values
        
        if self.view.selected_names:
            names_str = ", ".join(self.view.selected_names)
            
            await interaction.edit_original_response(
                embed=Embed(
                    description=get_localised_string(self.locale, "ui_birthday_remove_selected", names_str),
                    colour=Colour.green()
                ), 
                view=None
            )
        
        self.view.stop()
