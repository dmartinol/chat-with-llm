import logging
from pathlib import Path

from openai import OpenAI

from defaults import default_system_prompt, default_temperature
from message import Message

logger = logging.getLogger(__name__)


class ChatBot:
    def __init__(
        self, system_prompt=default_system_prompt, temperature=default_temperature
    ):
        self._client: OpenAI | None = None
        self._host: str | None = None
        self._history: list[Message] = []
        self._openai_model = "gpt-3.5-turbo"
        self.set_system_prompt(system_prompt)
        self.set_temperature(temperature)

    def _build_client(self):
        self._client = OpenAI(
            base_url="http://{host}:{port}/v1".format(host=self._host, port=8000),
        )

    def set_server(self, host: str):
        self._host = host
        self._build_client()

    @property
    def host(self) -> str:
        return self._host

    def set_system_prompt(self, system_prompt) -> None:
        self._system_prompt = system_prompt
        self._history = [m for m in self._history if not m.is_system_role()]
        self._history.append(Message().with_system_role().with_content(system_prompt))

    @property
    def system_prompt(self) -> str:
        return self._system_prompt

    def set_temperature(self, temperature) -> None:
        self._temperature = temperature

    @property
    def temperature(self) -> float:
        return self._temperature

    def send_user_request(self, request: str) -> any:
        if len(self._history) > 0 and self._history[-1].is_user_role():
            logger.warning("Removing latest user message to avoid duplications")
            self._history.pop()

        message = Message().with_user_role().with_content(request)
        self._history.append(message)
        logger.debug(f"history: {[m.dict for m in self._history]}")

        if self._client is None or self.connected_model() is None:
            return None

        create_params = {}
        create_params["temperature"] = self._temperature
        return self._client.chat.completions.create(
            model=self._openai_model,
            messages=[m.dict for m in self._history],
            stream=True,
            **create_params,
        )

    def add_response(self, response) -> None:
        self._history.append(Message().with_assistant_role().with_content(response))

    def clear(self) -> None:
        self._history.clear()

    def connected_model(self) -> str:
        if self._client is not None:
            try:
                models = self._client.models.list()
                logger.debug(models.data)
                if len(models.data) > 0:
                    return Path(models.data[0].id).name.upper()
                else:
                    logger.warning(
                        "No models available or an issue with the connection."
                    )
            except Exception as e:
                raise e
        return None
