"""
Integration with LLMs
"""

import json
import aiohttp
import logging

import globalconf as _globalconf
from . import botconf as _botconf

import discord

logger = logging.getLogger(__name__)


async def generate_response(
    message: discord.Message,
    system_prompt: str = _botconf.botconfig.system_prompt,
    # TODO: Use this again
    auto_pull_model: bool = _botconf.botconfig.auto_pull_model
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

        async with aiohttp.ClientSession() as cs:
            try:
                async with cs.post(url, json={
                    "model": _botconf.botconfig.llm_model,
                    "stream": False,
                    "messages": [
                        {"role": "system",
                            "content": system_prompt},
                        {"role": "user",
                            "content": message.content},
                    ],
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
