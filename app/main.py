"""
The main entrypoint to the bot
"""

import os
import logging

from dotenv import load_dotenv

# -------- Config --------
import globalconf
from logtools import log_print

# Load .env variables into environment
load_dotenv()

# Setup logger
logger = logging.getLogger(__name__)

log_level = os.getenv("LOG_LEVEL")
print(f"Log level var: {log_level}")
if log_level is not None and log_level.upper() not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
    print("log level is not valid")
    log_level = None

globalconf.LOG_LEVEL = log_level

print(f"globalconf.LOG_LEVEL: {globalconf.LOG_LEVEL}")

logging.basicConfig(
    level=globalconf.LOG_LEVEL
)

# Load configuration from environment
globalconf.DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if globalconf.DISCORD_TOKEN is None or globalconf.DISCORD_TOKEN == "":
    log_print("Error: DISCORD_TOKEN must be set in environment")
    exit(1)

discord_guild = os.getenv("DISCORD_GUILD")
if discord_guild is None or discord_guild == "":
    globalconf.DISCORD_GUILD = None
else:
    try:
        globalconf.DISCORD_GUILD = int(discord_guild)
    except:
        globalconf.DISCORD_GUILD = None

# The root directory should be the top level directory in this repo
log_print(f"ROOT_DIR: {os.path.abspath(globalconf.ROOT_DIR)}")

log_print(f"DATA_DIR: {os.path.abspath(globalconf.DATA_DIR)}")

if not os.path.exists(globalconf.DATA_DIR):
    os.mkdir(globalconf.DATA_DIR) # Ensure data directory is present

log_print(f"DB_FILE: {os.path.abspath(globalconf.DB_FILE)}")

log_print(f"CONFIG_FILE: {os.path.abspath(globalconf.CONFIG_FILE)}")
log_print(f"DEFAULT_CONFIG_FILE: {os.path.abspath(globalconf.DEFAULT_CONFIG_FILE)}")

# Create file if it doesn't exist
if not os.path.exists(globalconf.CONFIG_FILE):
    log_print(f"file doesn't exist: {globalconf.CONFIG_FILE}, creating...")
    open(globalconf.CONFIG_FILE, "a")

# LLM Server Config
llm_host = os.getenv("LLM_HOST")
if not llm_host is None:
    globalconf.LLM_HOST = llm_host

llm_port = os.getenv("LLM_PORT")
if not llm_port is None:
    try:
        globalconf.LLM_PORT = int(llm_port)
    except:
        globalconf.LLM_PORT = 11434

log_print("LLM:")
log_print(f"Host: {globalconf.LLM_HOST}")
log_print(f"Port: {globalconf.LLM_PORT}")

# -------- Main --------

# Import internal modules that depend on configuration after changes
import bot # TODO: Why can't I do `from . import bot`?
from bot import botconf

with open(globalconf.CONFIG_FILE, "r") as f:
    botconf.botconfig.load_from_file(f)

# Run bot
try:
    bot.client.run(globalconf.DISCORD_TOKEN)
except KeyboardInterrupt:
    log_print("Ctrl-C") # Exit cleanly in case of a KeyboardInterrupt
