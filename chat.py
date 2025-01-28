import logging

from message import Message

logger = logging.getLogger(__name__)
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

    def _append(self, message: Message) -> Message:
        self._history.append(message)
        return message

    def add_command(
        self, command: str, response: str, error: Exception | None = None
    ) -> Message:
        self._append(Message().with_user_role().with_content(command))
        if error is not None:
            error_message = (
                f"⚠️ {response}: {str(error if error is not None else 'Unknown error')}"
            )
            return self._append(
                Message()
                .with_app_role()
                .with_content(error_message)
                .with_error_severity()
            )
        return self._append(Message().with_app_role().with_content(response))

    def add_welcome_message(self, message: str) -> Message:
        return self._append(Message().with_app_role().with_content(message))

    def add_user_message(self, message: str) -> Message:
        return self._append(Message().with_user_role().with_content(message))

    def add_alert_message(self, message: str) -> Message:
        return self._append(Message().with_app_role().with_content(f"⚠️ {message}"))

    def add_response_message(self, response: str) -> Message:
        return self._append(Message().with_assistant_role().with_content(response))

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
