from enum import Enum


class Severity(str, Enum):
    INFO = ("INFO",)
    WARNING = ("WARNING",)
    ERROR = ("ERROR",)


class Message:
    def __init__(
        self,
    ):
        self._message: dict = {"state": Severity.INFO}

    @property
    def role(self) -> str:
        return self._message.get("role", "-")

    @property
    def content(self) -> str:
        return self._message.get("content", "-")

    @property
    def dict(self) -> dict:
        return self._message

    def with_system_role(self) -> "Message":
        self._message["role"] = "system"
        return self

    def with_user_role(self) -> "Message":
        self._message["role"] = "user"
        return self

    def with_assistant_role(self) -> "Message":
        self._message["role"] = "assistant"
        return self

    def with_app_role(self) -> "Message":
        self._message["role"] = "app"
        return self

    def with_content(self, content: str) -> "Message":
        self._message["content"] = content
        return self

    def with_warning_severity(self) -> "Message":
        self._message["severity"] = Severity.WARNING
        return self

    def with_error_severity(self) -> "Message":
        self._message["severity"] = Severity.ERROR
        return self

    def is_system_role(self) -> bool:
        return self._message.get("role", "") == "system"

    def is_user_role(self) -> bool:
        return self._message.get("role", "") == "user"

    def is_chat_message(self) -> bool:
        return self._message.get("role", "") in ["user", "assistant", "system"]

    _command_template = """
    >> {command}

    ========================

    {message}
    """

    @staticmethod
    def from_command(command: str, message: str) -> "Message":
        return (
            Message()
            .with_app_role()
            .with_content(
                Message._command_template.format(command=command, message=message)
            )
        )
