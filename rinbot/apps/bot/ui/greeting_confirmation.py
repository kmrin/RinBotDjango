from discord import Interaction, Embed, Colour, ButtonStyle
from discord.ui import View, Button, button as btn

from ..managers.locale import get_interaction_locale, get_localised_string


class GreetingConfirmation(View):
    def __init__(self, original_interaction: Interaction) -> None:
        super().__init__(timeout=60)

        locale = get_interaction_locale(original_interaction)

        self.original_interaction = original_interaction
        self.response = False

        self.confirm_embed = Embed(
            description=get_localised_string(
                locale, "ui_set_greeting_aproved",
            ),
            colour=Colour.green()
        )
        self.cancel_embed = Embed(
            description=get_localised_string(
                locale, "ui_set_greeting_reproved",
            ),
            colour=Colour.gold()
        )

        self._confirm.label = get_localised_string(locale, "ui_set_greeting_confirm_label")
        self._cancel.label = get_localised_string(locale, "ui_set_greeting_cancel_label")

    async def on_timeout(self) -> None:
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

        self.response = False
        self.stop()

        await interaction.edit_original_response(
            content=None, embed=self.cancel_embed, view=None
        )
