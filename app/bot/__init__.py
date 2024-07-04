import logging

import discord
from discord import app_commands

import globalconf as _globalconf
from . import botconf as _botconf
from . import bothist as _bothist
from . import llm
from . import botcmds as _botcmds

logger = logging.getLogger(__name__)

_intents = discord.Intents.default()
_intents.message_content = True

client = discord.Client(intents=_intents)
tree = app_commands.CommandTree(client)


# ---- Internal Helper Functions ----


def _in_guild(message: discord.Message) -> bool:
    # If no guild specified, then it is "In the guild"
    if _globalconf.DISCORD_GUILD is None:
        return True

    # If it is a private message, then it has no guild, and thus
    # cannot be in the correct one
    if message.guild is None:
        return False

    # Return whether the messaged guild and the global guild are the same
    return message.guild.id == _globalconf.DISCORD_GUILD


def _split_text(text: str, max_len: int = 2000) -> list[str]:
    """
    Split text into <=max_len character chunks

    text: Text to be split
    max_len: Maximum number of characters per chunk, 2000 by default
    (the Discord maximum message length)
    """
    if len(text) <= max_len:
        return [text]

    split_text = []
    while True:
        idx = text.rfind(" ", 0, max_len+1)
        if idx == -1:
            idx = max_len

        new = text[0:idx]
        split_text.append(new.strip())

        text = text[idx:]

        if len(text) <= max_len:
            split_text.append(text.strip())
            return split_text


# ---- App Commands ----


tree.add_command(_botcmds.help)

tree.add_command(_botcmds.resources)


# ---- Event handlers ----


@client.event
async def on_ready():
    guild = None
    if _globalconf.DISCORD_GUILD is not None:
        guild = discord.Object(id=_globalconf.DISCORD_GUILD)

    logger.info(f"Guild ID: {_globalconf.DISCORD_GUILD}")
    logger.info(f"{guild}")

    logger.info("syncing commands...")
    await tree.sync(guild=guild)
    logger.info("done syncing.")
    logger.info(f"Logged in as {client.user}")


@client.event
async def on_message(message: discord.Message):
    # Don't respond to messages from different guilds if it is enforced
    if not _in_guild(message):
        if _botconf.bot_config.enforce_guild:
            return

    # Don't respond to this bot's own messages
    if message.author == client.user:
        return

    # Add message to history
    _bothist.bot_history.add_message([message])

    if client.user in message.mentions:
        logger.info("received message")

        response = await llm.generate_response(
            message,
            _botconf.bot_config.system_prompt,
        )
        logger.info(f"response: `{response}`")
        if response is not None:
            if len(response) > 2000:
                # Split message into <=2000 character chunks
                message_chunks: list[discord.Message] = []
                for response_chunk in _split_text(response):
                    message_chunks.append(await message.reply(response_chunk))

                _bothist.bot_history.add_message(
                    message_chunks,
                    is_bot=True,
                )
            else:
                # Reply to the message, and add the reply to the history
                _bothist.bot_history.add_message(
                    [await message.reply(response)],
                    is_bot=True,
                )

            await client.change_presence(status=discord.Status.online)
        else:
            await client.change_presence(status=discord.Status.idle)
        return
    logger.info("message didn't mention the bot")
