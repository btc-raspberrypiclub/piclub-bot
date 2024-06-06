"""
Integration with LLMs
"""

import json
import aiohttp
import logging
logger = logging.getLogger(__name__)

import globalconf as _globalconf
from . import botconf as _botconf

import discord

async def generate_response(
    message: discord.Message,
    system_prompt: str = _botconf.botconfig.system_prompt,
    auto_pull_model: bool = _botconf.botconfig.auto_pull_model # TODO: Use this again
) -> str | None:
    url = f"http://{_globalconf.LLM_HOST}:{_globalconf.LLM_PORT}/api/chat"
    logger.info(f"url: {url}")

    # While receiving responses, show typing status
    async with message.channel.typing():
        logger.info(f"Generating response ...\nSystem prompt:\n{system_prompt}\nUser prompt:\n{message.content}")

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


#def pull_model(model: str):
    #log_print(f"Pulling model: {model} ...")
    #r = requests.post(
        #f"http://{_globalconf.LLM_HOST}:{_globalconf.LLM_PORT}/api/pull",
        #json={
            #"name": model,
            #"stream": False,
        #},
    #)

    #r.raise_for_status()
    #log_print(r.json())
