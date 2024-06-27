import random
import logging

import discord

import globalconf as _globalconf
from . import botconf as _botconf
from . import bothist as _bothist
from . import llm

logger = logging.getLogger(__name__)

_intents = discord.Intents.default()
_intents.message_content = True

client = discord.Client(intents=_intents)


def _is_command(text: str) -> bool:
    return text.startswith(_botconf.bot_config.command_prefix)


def _is_greeting(message: discord.Message) -> bool:
    has_greeting_prefix = False
    for greeting in _botconf.bot_config.greetings:
        if message.content.lower().startswith(greeting):
            has_greeting_prefix = True
            break

    if not has_greeting_prefix:
        return False

    return client.user in message.mentions


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


async def _handle_command(
    command: str,
    args: list[str],
    message: discord.Message,
):
    response = ""
    pre = _botconf.bot_config.command_prefix
    match command.lower():
        case "help" | "h":
            response += (
                "```\n" +
                pre+"help       " + pre+"h  -  " + "show this help message\n" +
                pre+"resources  " + pre+"r  -  " + "list resources\n" +
                "```"
            )

        case "resources" | "r":
            if len(_botconf.bot_config.resources) == 0:
                response += "There are currently no resources"
            else:
                for r in _botconf.bot_config.resources:
                    response += "- " + str(r) + "\n"
        case _:
            response += "Unknown command. Type `" + pre+"help` for help"

    await message.channel.send(response, suppress_embeds=True)


@client.event
async def on_ready():
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

    if _is_command(message.content):
        logger.info("received command")
        split_message = message.content.strip(" \t\n").split()
        command = split_message[0][len(_botconf.bot_config.command_prefix):]
        args = split_message[1:]

        await _handle_command(command, args, message)
        return

    # Add message to history
    _bothist.bot_history.add_message(message)

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
                for response_chunk in _split_text(response):
                    _bothist.bot_history.add_message(
                        await message.reply(response_chunk),
                        is_bot=True,
                    )
            else:
                # Reply to the message, and add the reply to the history
                _bothist.bot_history.add_message(
                    await message.reply(response),
                    is_bot=True,
                )

            await client.change_presence(status=discord.Status.online)
        else:
            await client.change_presence(status=discord.Status.idle)
        return
