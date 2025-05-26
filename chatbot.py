import logging
import os
from typing import Generator

from ollama import Client as OllamaClient
from openai import OpenAI

from defaults import default_system_prompt, default_temperature
from message import Message

logger = logging.getLogger("chatbot")

_OPENAI_HOST = "https://api.openai.com/v1"
_OPENAI_MODEL = "gpt-4o"


class ChatBot:
    def __init__(
        self, system_prompt=default_system_prompt, temperature=default_temperature
    ):
        self._client: OpenAI | OllamaClient | None = None
        self._host: str | None = None
        self._ollama_enabled = False
        self._history: list[Message] = []
        self._model_name = _OPENAI_MODEL
        self.set_system_prompt(system_prompt)
        self.set_temperature(temperature)
        self.set_host(_OPENAI_HOST)

    def _build_client(self):
        if self._host is None:
            self._client = None
            return

        if self._ollama_enabled:
            if "https" in self._host:
                base_url = self._host
            else:
                if ":" in self._host:
                    host, port = self._host.split(":")
                else:
                    host = self._host
                    port = self._default_port
                base_url = f"http://{host}:{port}"
            logger.info(f"Building Ollama client with base URL: {base_url}")
            self._client = OllamaClient(host=base_url)
        else:
            if os.getenv("OPENAI_API_KEY"):
                logger.info(f"Building OpenAI client with base URL: {_OPENAI_HOST}")
                self._client = OpenAI(
                    base_url=_OPENAI_HOST, api_key=os.getenv("OPENAI_API_KEY")
                )

        self._model_name = (
            self._models()[0] if self._ollama_enabled else self._default_model
        )

    @property
    def _default_port(self) -> int:
        return 11434 if self._ollama_enabled else 8000

    @property
    def _default_model(self) -> str:
        return _OPENAI_MODEL if not self._ollama_enabled else ""

    def set_host(self, host: str):
        self._host = host
        self._build_client()

    @property
    def host(self) -> str:
        return self._host

    def toggle_ollama_support(self) -> None:
        self._ollama_enabled = not self._ollama_enabled
        if self._ollama_enabled:
            self.set_host(None)
        else:
            self.set_host(_OPENAI_HOST)

    @property
    def ollama_enabled(self) -> bool:
        return self._ollama_enabled

    def set_system_prompt(self, system_prompt) -> None:
        self._system_prompt = system_prompt
        self._history = [m for m in self._history if not m.is_system_role()]
        self.append(Message.from_system_prompt(system_prompt))

    @property
    def system_prompt(self) -> str:
        return self._system_prompt

    def set_temperature(self, temperature) -> None:
        self._temperature = temperature

    @property
    def temperature(self) -> float:
        return self._temperature

    def send_user_request(self, request: str) -> Generator:
        if len(self._history) > 0 and self._history[-1].is_user_role():
            logger.warning("Removing latest user message to avoid duplications")
            self._history.pop()

        message = Message.from_user_message(request)
        self.append(message)
        logger.debug(f"history: {[m.dict for m in self._history]}")

        if self._client is None:
            return None

        create_params = {}
        create_params["temperature"] = self._temperature

        if self._ollama_enabled:
            stream = self._client.chat(
                model=self._model_name,
                messages=[m.dict for m in self._history],
                stream=True,
                options=create_params,
            )

            for chunk in stream:
                if chunk["message"]["content"]:
                    yield chunk["message"]["content"]
        else:
            stream = self._client.chat.completions.create(
                model=self._model_name,
                messages=[m.dict for m in self._history],
                stream=True,
                **create_params,
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

    def append(self, message: Message) -> Message:
        self._history.append(message)
        return message

    def clear(self) -> None:
        self._history.clear()

    def connected_model(self) -> str:
        if not self._ollama_enabled:
            return self._default_model
        if self._client is not None:
            try:
                models = self._models()
                if len(models) > 0:
                    return models[0]
                else:
                    logger.warning(
                        "No models available or an issue with the connection."
                    )
                    return ["NA"]
            except Exception as e:
                raise e
        return None

    def _models(self) -> list[str]:
        if self.ollama_enabled:
            try:
                models = self._client.ps()
                logger.info(f"Ollama models are {models}")
                return [m["name"] for m in models["models"]]
            except Exception as e:
                logger.error(f"Error fetching Ollama models: {e}")
                return []
        else:
            return [self._default_model]
        return []
