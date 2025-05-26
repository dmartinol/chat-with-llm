import logging

from message import Message

logger = logging.getLogger("chatbot")
_help_message = """
            Help / TL;DR
            - /c <host>: Connect OpenAI-compliant server host
            - /c: Print connected server host
            - /h: Print this help message
            - /s: Print system prompt
            - /s <prompt>: Initialize system prompt
            """


class Chat:
    def __init__(self):
        self._history: list[Message] = []

    def append(self, message: Message) -> Message:
        self._history.append(message)
        return message

    def append_all(self, messages: list[Message]):
        self._history.extend(messages)

    def messages(self) -> list[Message]:
        return self._history

    def clear(self) -> None:
        self._history.clear()

    def history_messages(self) -> list[Message]:
        return [m for m in self._history if m.is_user_role()]

    def delete_from_history(self, message) -> list[Message]:
        self._history.remove(message)

    def delete_history(self):
        self._history.clear()
