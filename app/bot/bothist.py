import discord

from . import botconf as _botconf


class MessageHistory:
    message_histories: dict[int, list[dict[str, str]]]
    """A dictionary that associates channel IDs to their histories"""

    def __init__(self) -> None:
        self.message_histories = {}

    def add_message(
        self,
        message: discord.Message,
        is_bot: bool = False
    ) -> None:
        # Create message dict
        msg_dict = {
            "role": "assistant" if is_bot else "user",
            "content":
                # Add author name and mention to content if it is not a bot
                ("" if is_bot else
                 f"({message.author.display_name} {message.author.mention})") +
                f" {message.content}"
        }

        chan_id = message.channel.id
        hist_len = _botconf.bot_config.history_length
        if chan_id in self.message_histories:
            self.message_histories[chan_id].append(msg_dict)
            if len(self.message_histories[chan_id]) > hist_len:
                # Truncate the channel's history to the last
                # `history_length` messages
                self.message_histories[chan_id] = (
                    self.message_histories[chan_id][-hist_len:]
                )
        else:
            self.message_histories[chan_id] = [msg_dict]


bot_history = MessageHistory()
