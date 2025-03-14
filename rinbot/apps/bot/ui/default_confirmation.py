from discord import Interaction, Embed, Colour, ButtonStyle
from discord.ui import View, Button, button as btn
from typing import Optional

from ..managers.locale import get_interaction_locale, get_localised_string


class DefaultConfirmation(View):
    def __init__(
            self,
            interaction: Interaction,
            confirm_embed: Embed,
            cancel_embed: Optional[Embed] = None
    ) -> None:
        super().__init__(timeout=60.0)

        self.interaction = interaction
        self.confirm_embed = confirm_embed
        self.cancel_embed = cancel_embed
        
        locale = get_interaction_locale(interaction)
        
        if not cancel_embed:
            self.cancel_embed = Embed(
                description=get_localised_string(locale, "ui_generic_cancel_embed_desc"),
                colour=Colour.red()
            )
        
        self._confirm.label = get_localised_string(locale, "ui_button_yes")
        self._cancel.label = get_localised_string(locale, "ui_button_no")
    
    async def on_timeout(self):
        self.stop()
    
    @btn(label="", style=ButtonStyle.green)
    async def _confirm(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.defer()

        self.response = True
        self.stop()

        await interaction.edit_original_response(
            content=None, embed=self.confirm_embed, view=None
        )

    @btn(label="", style=ButtonStyle.red)
    async def _cancel(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.defer()

        self.stop()

        await interaction.edit_original_response(
            content=None, embed=self.cancel_embed, view=None
        )
