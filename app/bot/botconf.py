from typing import Any
import logging
logger = logging.getLogger(__name__)

import yaml

import globalconf as _globalconf


class Resource:
    """
    Represents a resource that can be listed with the `!resource` command
    """
    name: str
    link: str
    desc: str


    def __init__(self, name: str, link: str, desc: str):
        self.name = name
        if not link.startswith("https://") and not link.startswith("http://"):
            link = "https://" + link
        self.link = link
        self.desc = desc


    def __str__(self) -> str:
        s = f"[{self.name}]({self.link})"
        if self.desc != "":
            s += f": {self.desc}"
        return s


class BotConfig:
    command_prefix: str
    greetings: list[str]
    enforce_guild: bool
    resources: list[Resource]
    bot_name: str
    llm_enabled: bool
    llm_model: str
    auto_pull_model: bool
    system_prompt: str


    def __init__(self):
        self.command_prefix = "!"
        self.greetings = ["hello", "hi", "hey"]
        self.enforce_guild = True
        self.resources = []
        self.bot_name = ""
        self.llm_enabled = False
        self.llm_model = "llama2"
        self.auto_pull_model = False
        self.system_prompt = ""


    def load_from_file(self, f):
        user_config = yaml.load(f, yaml.Loader)

        with open(_globalconf.DEFAULT_CONFIG_FILE, "r") as default_config_file:
            default_config = yaml.load(default_config_file, yaml.Loader)

        # This will raise an exception if default_config is malformed
        merged_config = _merge_configs(user_config, default_config)

        self.command_prefix  = merged_config["command_prefix"]
        self.greetings       = merged_config["greetings"]
        self.enforce_guild   = merged_config["enforce_guild"]
        self.resources       = merged_config["resources"]
        self.bot_name        = merged_config["bot_name"]
        self.llm_enabled     = merged_config["llm_enabled"]
        self.llm_model       = merged_config["llm_model"]
        self.auto_pull_model = merged_config["auto_pull_model"]
        self.system_prompt   = merged_config["system_prompt"]

        logger.debug(f"Merged Config:\n{yaml.dump(merged_config)}")


def _has_key_of_type(d: Any, k: str, t: type) -> bool:
    """
    Check if a dict `d` has a key `k` of type `t`
    """
    return k in d and isinstance(d[k], t)

def _all_isinstance(l: Any, t: type) -> bool:
    if not isinstance(l, list):
        return False

    for e in l:
        if not isinstance(e, t):
            return False

    return True

def _merge_configs(user_config: Any, default_config: Any) -> dict[Any, Any]:
    """
    Will raise an exception if default_config is
    missing a value, or the value is of the wrong type
    """

    if default_config is None:
        raise Exception("default_config is None")

    if user_config is None:
        user_config = {}

    merged_config = {}

    if not _has_key_of_type(default_config, "command_prefix", str):
        raise Exception("default_config is missing a key `command_prefix`")
    if _has_key_of_type(user_config, "command_prefix", str):
        merged_config["command_prefix"] = user_config["command_prefix"]
    else:
        merged_config["command_prefix"] = default_config["command_prefix"]

    if not ("greetings" in default_config and _all_isinstance(default_config["greetings"], str)):
        raise Exception("default_config is missing a key `greetings`")
    if "greetings" in user_config and _all_isinstance(user_config["greetings"], str):
        merged_config["greetings"] = user_config["greetings"]
    else:
        merged_config["greetings"] = default_config["greetings"]


    if not _has_key_of_type(default_config, "enforce_guild", bool):
        raise Exception("default_config is missing a key `enforce_guild`")
    if _has_key_of_type(user_config, "enforce_guild", bool):
        merged_config["enforce_guild"] = user_config["enforce_guild"]
    else:
        merged_config["enforce_guild"] = default_config["enforce_guild"]

    merged_config["resources"] = []
    if not _has_key_of_type(default_config, "resources", list):
        raise Exception("default_config is missing a key `resources`")
    if _has_key_of_type(user_config, "resources", list):
        for res in user_config["resources"]:
            if "name" not in res or "link" not in res:
                logger.warning(f"Malformed resource: {res}")
                continue

            if "desc" not in res:
                res["desc"] = ""

            merged_config["resources"].append(
                Resource(res["name"], res["link"], res["desc"])
            )
    else:
        for res in default_config["resources"]:
            if "name" not in res or "link" not in res:
                logger.warning(f"Malformed resource: {res}")
                continue

            if "desc" not in res:
                res["desc"] = ""

            merged_config["resources"].append(
                Resource(res["name"], res["link"], res["desc"])
            )

    if not _has_key_of_type(default_config, "bot_name", str):
        raise Exception("default_config is missing a key `bot_name`")
    if _has_key_of_type(user_config, "bot_name", str):
        merged_config["bot_name"] = user_config["bot_name"]
    else:
        merged_config["bot_name"] = default_config["bot_name"]

    if not _has_key_of_type(default_config, "llm_enabled", bool):
        raise Exception("default_config is missing a key `llm_enabled`")
    if _has_key_of_type(user_config, "llm_enabled", bool):
        merged_config["llm_enabled"] = user_config["llm_enabled"]
    else:
        merged_config["llm_enabled"] = default_config["llm_enabled"]

    if not _has_key_of_type(default_config, "llm_model", str):
        raise Exception("default_config is missing a key `llm_model`")
    if _has_key_of_type(user_config, "llm_model", str):
        merged_config["llm_model"] = user_config["llm_model"]
    else:
        merged_config["llm_model"] = default_config["llm_model"]

    if not _has_key_of_type(default_config, "auto_pull_model", bool):
        raise Exception("default_config is missing a key `auto_pull_model`")
    if _has_key_of_type(user_config, "auto_pull_model", bool):
        merged_config["auto_pull_model"] = user_config["auto_pull_model"]
    else:
        merged_config["auto_pull_model"] = default_config["auto_pull_model"]

    if not _has_key_of_type(default_config, "system_prompt", str):
        raise Exception("default_config is missing a key `system_prompt`")
    if _has_key_of_type(user_config, "system_prompt", str):
        # FIXME: This is a bad place to put the information about commands
        name_prompt = "" if merged_config["bot_name"] == "" else f" Your name is {merged_config['bot_name']}."
        merged_config["system_prompt"] = user_config["system_prompt"] +\
            name_prompt +\
            f" You can help people if they run the command `{merged_config['command_prefix']}help`." +\
            f" You can give information about resources if they type the command `{merged_config['command_prefix']}resources`."
    else:
        name_prompt = "" if merged_config["bot_name"] == "" else f" Your name is {merged_config['bot_name']}."
        merged_config["system_prompt"] = default_config["system_prompt"] +\
            name_prompt +\
            f" You can help people if they run the command `{merged_config['command_prefix']}help`." +\
            f" You can give information about resources if they type the command `{merged_config['command_prefix']}resources`."


    return merged_config

botconfig = BotConfig()
