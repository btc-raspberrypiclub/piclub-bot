"""
The main entrypoint to the bot
"""

import os
import logging

from dotenv import load_dotenv

# -------- Config --------
import globalconf

# Load .env variables into environment
load_dotenv()

# Setup logger
logger = logging.getLogger(__name__)

log_level = os.getenv("LOG_LEVEL")
if (log_level is not None and log_level.upper()
        not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")):
    print(f"LOG_LEVEL `{log_level}` is invalid")
    log_level = None

globalconf.LOG_LEVEL = log_level

logging.basicConfig(
    level=globalconf.LOG_LEVEL
)
if globalconf.LOG_LEVEL is not None:
    logger.setLevel(globalconf.LOG_LEVEL)

logger.info(f"LOG_LEVEL={globalconf.LOG_LEVEL}")

# Load configuration from environment
globalconf.DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if globalconf.DISCORD_TOKEN is None or globalconf.DISCORD_TOKEN == "":
    logger.critical("DISCORD_TOKEN must be set in environment")
    exit(1)

discord_guild = os.getenv("DISCORD_GUILD")
if discord_guild is None or discord_guild == "":
    globalconf.DISCORD_GUILD = None
else:
    try:
        globalconf.DISCORD_GUILD = int(discord_guild)
    except ValueError:
        logger.warning(
            "DISCORD_GUILD is an invalid integer. Defaulting to None"
        )
        globalconf.DISCORD_GUILD = None

# The root directory should be the top level directory in this repo
logger.info(f"ROOT_DIR={os.path.abspath(globalconf.ROOT_DIR)}")

logger.info(f"DATA_DIR={os.path.abspath(globalconf.DATA_DIR)}")

if not os.path.exists(globalconf.DATA_DIR):
    os.mkdir(globalconf.DATA_DIR)  # Ensure data directory is present

logger.info(f"DB_FILE={os.path.abspath(globalconf.DB_FILE)}")

logger.info(f"CONFIG_FILE={os.path.abspath(globalconf.CONFIG_FILE)}")
logger.info(
    f"DEFAULT_CONFIG_FILE={os.path.abspath(globalconf.DEFAULT_CONFIG_FILE)}"
)

# Create file if it doesn't exist
if not os.path.exists(globalconf.CONFIG_FILE):
    logger.info(f"file doesn't exist: {globalconf.CONFIG_FILE}, creating...")
    open(globalconf.CONFIG_FILE, "a")

# LLM Server Config
llm_host = os.getenv("LLM_HOST")
if llm_host is not None:
    globalconf.LLM_HOST = llm_host

llm_port = os.getenv("LLM_PORT")
if llm_port is not None:
    try:
        globalconf.LLM_PORT = int(llm_port)
    except ValueError:
        globalconf.LLM_PORT = 11434

logger.info(f"LLM_HOST={globalconf.LLM_HOST}")
logger.info(f"LLM_PORT={globalconf.LLM_PORT}")

# -------- Main --------

# Import internal modules that depend on configuration after changes
import bot  # TODO: Why can't I do `from . import bot`?
from bot import botconf

with open(globalconf.CONFIG_FILE, "r") as f:
    botconf.botconfig.load_from_file(f)

# Run bot
try:
    bot.client.run(
        globalconf.DISCORD_TOKEN,
        log_handler=None,
    )
except KeyboardInterrupt:
    print("Ctrl-C: Exiting")  # Exit cleanly in case of a KeyboardInterrupt
