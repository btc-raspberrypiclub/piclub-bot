"""
Integration with LLMs
"""

import json
import aiohttp

import globalconf as _globalconf
from logtools import log_print
from . import botconf as _botconf

import discord

conversation_history = []

# FIXME: This will probably have race condition issues, GL HF :)
def update_conversation_history(user_message, bot_response):
    # Append the new user message and bot response to the conversation history
    conversation_history.append({"role": "user", "content": user_message})
    conversation_history.append({"role": "bot", "content": bot_response})

    # Optionally, limit the history length to the last N messages
    if len(conversation_history) > 20:
        conversation_history = conversation_history[-20:]

# TODO: Add support for multiple channels
def context_from_conversation_history():
    context = ""
    for message in conversation_history:
        context += f"{message['role']}: {message['content']}\n"
    return context

async def generate_response_with_context(message):
    context = context_from_conversation_history()

    response = await llm.generate_response(
        _botconf.botconfig.system_prompt +
        f" The user's name is {message.author.name}" +
        context +
        f"user: {message}\nbot:"
    )

    return response

async def generate_response(
    message: discord.Message,
    system_prompt: str = _botconf.botconfig.system_prompt,
    auto_pull_model: bool = _botconf.botconfig.auto_pull_model # TODO: Use this again
) -> str | None:
    url = f"http://{_globalconf.LLM_HOST}:{_globalconf.LLM_PORT}/api/generate"
    log_print(f"url: {url}")

    # While receiving responses, show typing status
    async with message.channel.typing():
        log_print(f"Generating response ...\nUser prompt:\n{message.content}\nSystem prompt:\n{system_prompt}")

        async with aiohttp.ClientSession() as cs:
            try:
                async with cs.post(url, json={
                    "model": _botconf.botconfig.llm_model,
                    "prompt": message.content,
                    "system": system_prompt,
                    "context": [],
                    "stream": False,
                }) as res:
                    data = await res.json()
                    if "error" in data:
                        log_print(f"Error: {data['error']}")
                        log_print(f"data: {json.dumps(data)}")
                        return None

                    dur = data["total_duration"] / 1_000_000_000
                    log_print(f"response took {dur:.3f} seconds")

                    return data["response"]


            except Exception as e:
                #err_res = e.response
                #if not isinstance(err_res, requests.models.Response):
                    #raise e

                log_print(f"Error: {e}\nType: {type(e)}")

                #if err_res.status_code == 404 and auto_pull_model:
                    #pull_model(_botconf.botconfig.llm_model)

                return None
            #except ConnectionError as e:
                #log_print(f"Ollama server unavailable at {url}")
                #return None

        #response = ""
            ## Loop through tokens as they are streamed in
        #for line in r.iter_lines():
            #body = json.loads(line) # Parse response as json

            ## Append token to response
            #response_part = body.get("response", "")
            #response += response_part

            ## Raise error if present
            #if "error" in body:
                #raise Exception(body["error"])

            ## Return response if done
            #if body.get("done", False):
                #log_print("Done typing (done)")
                #return response

        #log_print("Done typing (no more lines)")

        ## Return response
        #return None


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
