from discord import Interaction, Embed, Colour, ButtonStyle
from discord.ui import View, Button, button

from ..managers.locale import get_interaction_locale, get_localised_string


class WelcomeConfirmation(View):
    def __init__(self, original_interaction: Interaction) -> None:
        super().__init__(timeout=60)
        
        self.response: bool = None
        locale = get_interaction_locale(original_interaction)
        
        self.confirm_embed = Embed(
            description=get_localised_string(locale, "ui_wc_aproved"),
            colour=Colour.green()
        )
        self.deny_embed = Embed(
            description=get_localised_string(locale, "ui_wc_denied"),
            colour=Colour.yellow()
        )
        
        self._confirm.label = get_localised_string(locale, "ui_wc_confirm_label")
        self._cancel.label = get_localised_string(locale, "ui_wc_cancel_label")
    
    async def on_timeout(self) -> None:
        self.response = False
        self.stop()
    
    @button(label="", style=ButtonStyle.green)
    async def _confirm(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.defer()
        
        self.response = True
        self.stop()
        
        await interaction.edit_original_response(content=None, embed=self.confirm_embed, view=None)
    
    @button(label="", style=ButtonStyle.red)
    async def _cancel(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.defer()
        
        self.response = False
        self.stop()
        
        await interaction.edit_original_response(content=None, embed=self.deny_embed, view=None)
