from enum import Enum


class Severity(str, Enum):
    INFO = ("INFO",)
    WARNING = ("WARNING",)
    ERROR = ("ERROR",)

    def to_icon(self) -> str:
        if self == Severity.WARNING:
            return ":warning:"
        if self == Severity.ERROR:
            return ":bangbang:"
        return ""


class Message:
    def __init__(
        self,
    ):
        self._message: dict = {"severity": Severity.INFO}

    @property
    def role(self) -> str:
        return self._message.get("role", "-")

    @property
    def content(self) -> str:
        return self._message.get("content", "-").strip()

    @property
    def dict(self) -> dict:
        return self._message

    def to_markdown(self) -> str:
        return f"{self._message['severity'].to_icon()} {self.content}".strip()

    @staticmethod
    def from_response(response, error: Exception | None = None) -> "Message":
        message = Message()._with_assistant_role()._with_content(response)
        if error is not None:
            message = message._with_content(
                f"{response}: {str(error if error is not None else 'Unknown error')}"
            )._with_error_severity()
        return message

    @staticmethod
    def from_command(
        command: str, response: str, error: Exception | None = None
    ) -> list["Message"]:
        messages = [Message()._with_user_role()._with_content(command)]
        if error is not None:
            error_message = (
                f"{response}: {str(error if error is not None else 'Unknown error')}"
            )
            messages.append(
                Message()
                ._with_app_role()
                ._with_content(error_message)
                ._with_error_severity()
            )
        else:
            messages.append(Message()._with_app_role()._with_content(response))
        return messages

    @staticmethod
    def from_app_message(content) -> "Message":
        return Message()._with_app_role()._with_content(content)

    @staticmethod
    def from_user_message(content) -> "Message":
        return Message()._with_user_role()._with_content(content)

    @staticmethod
    def from_system_prompt(content) -> "Message":
        return Message()._with_system_role()._with_content(content)

    def _with_system_role(self) -> "Message":
        self._message["role"] = "system"
        return self

    def _with_user_role(self) -> "Message":
        self._message["role"] = "user"
        return self

    def _with_assistant_role(self) -> "Message":
        self._message["role"] = "assistant"
        return self

    def _with_app_role(self) -> "Message":
        self._message["role"] = "app"
        return self

    def _with_content(self, content: str) -> "Message":
        self._message["content"] = content
        return self

    def with_warning_severity(self) -> "Message":
        self._message["severity"] = Severity.WARNING
        return self

    def _with_error_severity(self) -> "Message":
        self._message["severity"] = Severity.ERROR
        return self

    def is_system_role(self) -> bool:
        return self._message.get("role", "") == "system"

    def is_user_role(self) -> bool:
        return self._message.get("role", "") == "user"
