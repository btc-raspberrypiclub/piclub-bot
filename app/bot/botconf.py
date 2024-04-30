import yaml

class Resource:
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
    resources: list[Resource]
    llm_enabled: bool
    auto_pull_model: bool
    system_prompt: str

    def __init__(self):
        self.command_prefix = "!"
        self.greetings = ["hello", "hi", "hey"]
        self.resources = []
        self.llm_enabled = False
        self.auto_pull_model = False
        self.system_prompt = ""

    def load_from_file(self, f):
        cfg_obj = yaml.load(f, yaml.Loader)
        if cfg_obj is None:
            return

        if "command_prefix" in cfg_obj and isinstance(cfg_obj["command_prefix"], str):
            self.command_prefix = cfg_obj["command_prefix"]

        if "greetings" in cfg_obj and isinstance(cfg_obj["greetings"], list):
            # Make sure all elements are strings
            for e in cfg_obj["greetings"]:
                if not isinstance(e, str):
                    return

            self.greetings = cfg_obj["greetings"]

        if "resources" in cfg_obj and isinstance(cfg_obj["resources"], list):
            for res in cfg_obj["resources"]:
                if "name" not in res or "link" not in res:
                    continue

                if "desc" not in res:
                    res["desc"] = ""

                self.resources.append(
                    Resource(res["name"], res["link"], res["desc"])
                )

        if "llm_enabled" in cfg_obj and isinstance(cfg_obj["llm_enabled"], bool):
            self.llm_enabled = cfg_obj["llm_enabled"]

        if "auto_pull_model" in cfg_obj and isinstance(cfg_obj["auto_pull_model"], bool):
            self.auto_pull_model = cfg_obj["auto_pull_model"]

        if "system_prompt" in cfg_obj and isinstance(cfg_obj["system_prompt"], str):
            self.system_prompt = cfg_obj["system_prompt"]


botconfig = BotConfig()