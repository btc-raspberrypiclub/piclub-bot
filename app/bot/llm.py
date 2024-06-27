"""
Integration with LLMs
"""

import json
import aiohttp
import logging

import globalconf as _globalconf
from . import botconf as _botconf
from . import bothist as _bothist

import discord

logger = logging.getLogger(__name__)


async def generate_response(
    message: discord.Message,
    system_prompt: str = _botconf.bot_config.system_prompt,
    # TODO: Use this again
    auto_pull_model: bool = _botconf.bot_config.auto_pull_model
) -> str | None:
    url = f"http://{_globalconf.LLM_HOST}:{_globalconf.LLM_PORT}/api/chat"
    logger.info(f"url: {url}")

    # While receiving responses, show typing status
    async with message.channel.typing():
        logger.info(
            "Generating response ...\n" +
            f"System prompt:\n{system_prompt}\n" +
            f"User prompt:\n{message.content}"
        )

        messages: list[dict[str, str]] = [
            {"role": "system", "content": system_prompt},
            *_bothist.bot_history.message_histories[message.channel.id],
        ]

        logger.info(", ".join([f"{{{msg['role'][0:1]}: '{msg['content'][0:10]}'}}" for msg in messages]))

        async with aiohttp.ClientSession() as cs:
            try:
                async with cs.post(url, json={
                    "model": _botconf.bot_config.llm_model,
                    "stream": False,
                    "messages": messages,
                }) as res:
                    data = await res.json()
                    if "error" in data:
                        logger.error(f"{data['error']}")
                        logger.info(f"data: {json.dumps(data)}")
                        return None

                    dur = data["total_duration"] / 1_000_000_000
                    logger.info(f"response took {dur:.3f} seconds")

                    return data["message"]["content"]

            except Exception as e:
                logger.error(f"{e}\nType: {type(e)}")

                return None
