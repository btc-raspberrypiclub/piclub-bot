import discord
from discord import app_commands
from .botconf import bot_config as _bot_config
from globalconf import DISCORD_GUILD

guilds: list[int] = []
if DISCORD_GUILD is not None:
    guilds.append(DISCORD_GUILD)


@app_commands.guilds(*guilds)
@app_commands.command(
    name="help",
    description="Print help for bot commands.",
)
async def help(interaction: discord.Interaction):
    await interaction.response.send_message(
        "```\n" +
        "/help       -  show this help message\n" +
        "/resources  -  list resources\n" +
        "```",
        ephemeral=True,
    )


@app_commands.guilds(*guilds)
@discord.app_commands.command(
    name="resources",
    description="Print the list of available resources.",
)
async def resources(interaction: discord.Interaction):
    response = ""
    if len(_bot_config.resources) == 0:
        response = "There are currently no resources"
    else:
        for r in _bot_config.resources:
            response += "- " + str(r) + "\n"

    await interaction.response.send_message(response)
