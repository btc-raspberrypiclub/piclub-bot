import discord

from . import botconf as _botconf


class MessageHistory:
    message_histories: dict[int, list[dict[str, str]]]
    """A dictionary that associates channel IDs to their histories"""

    def __init__(self) -> None:
        self.message_histories = {}

    # NOTE: This method can add messages out of order
    def add_message(
        self,
        message_list: list[discord.Message],
        is_bot: bool = False
    ) -> None:
        """
        Concatenate the contents of a list of messages into a
        single dictionary, and add it to the history.
        The resulting message dictionary will be added to the
        history of the first message's channel.
        The channel's message history will then be truncated
        to the length specified by `history_length` in the
        bot's config.
        If `is_bot` is True, the message's role will be
        "assistant", otherwise it will be "user".
        If `is_bot` is False, the message's content will also
        be prepended with `(user_name <@user_id>)`, where
        `user_name` is the author of the first message's display
        name, and `<@user_id>` is the text used to mention the
        author of the first message.
        """

        if len(message_list) < 1:
            return

        author = message_list[0].author
        content = (
            # Add author name and mention to content if it is not a bot
            "" if is_bot else f"({author.display_name} {author.mention}) "
        )
        content += " ".join([m.content for m in message_list])

        # Create message dict
        msg_dict = {
            "role": "assistant" if is_bot else "user",
            "content": content,
        }

        chan_id = message_list[0].channel.id
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
