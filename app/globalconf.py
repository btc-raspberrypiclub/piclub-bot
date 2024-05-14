import os as _os

# Discord config
DISCORD_TOKEN: str | None = None
DISCORD_GUILD: int | None = None

# File config
ROOT_DIR: str = _os.path.join(
    _os.path.abspath(_os.path.dirname(__file__)),
    _os.pardir,
)
DATA_DIR: str = _os.path.join(ROOT_DIR, "data")
DB_FILE: str = _os.path.join(DATA_DIR, "data.db")
CONFIG_FILE: str = _os.path.join(DATA_DIR, "config.yaml")
DEFAULT_CONFIG_FILE: str = _os.path.join(
    _os.path.dirname(__file__),
    "default-config.yaml",
)

# LLM server config
LLM_HOST: str = "localhost"
LLM_PORT: int = 11434

# Logging
LOG_LEVEL: str | None = None
