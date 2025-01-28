from typing import Callable

import streamlit as st

from defaults import help_message, welcome
from message import Message


def _help(request: str):
    st.session_state._chat.append_all(Message.from_command(request, help_message))


def _connect_server(request: str):
    if len(request.split(" ")) > 1:
        host = request.split(" ")[1]
        try:
            st.session_state._chatbot.set_server(host)
        except Exception as error:
            st.session_state._chat.append_all(
                Message.from_command(
                    request, response="Cannot configure server host", error=error
                )
            )
            return
    if st.session_state._chatbot.host is None:
        st.session_state._chat.append_all(
            Message.from_command(
                request, "No server host defined yet! Define one by using `/c <host>`"
            )
        )
    else:
        try:
            message = f"""
          Server host is: {st.session_state._chatbot.host}

          Connected model is: {st.session_state._chatbot.connected_model()}
          """
            st.session_state._chat.append_all(Message.from_command(request, message))
        except Exception as error:
            st.session_state._chat.append_all(
                Message.from_command(
                    request, response="Cannot fetch server details", error=error
                )
            )


def _system_prompt(request: str):
    if len(request.split(" ")) > 1:
        prompt = " ".join(request.split(" ")[1:]).strip()
        st.session_state._chatbot.set_system_prompt(prompt)

    st.session_state._chat.append_all(
        Message.from_command(
            request,
            f"**System prompt** is: '{st.session_state._chatbot.system_prompt}'",
        )
    )


def _temperature(request: str):
    if len(request.split(" ")) > 1:
        temperature = request.split(" ")[1]
        try:
            value = float(temperature)
            if 0 <= value <= 1:
                st.session_state._chatbot.set_temperature(value)
        except ValueError:
            st.session_state._chat.append_all(
                Message.from_command(
                    request,
                    "**Value error** sampling temperature must be a float in the range 0-1",
                )
            )
            return
    st.session_state._chat.append_all(
        Message.from_command(
            request,
            f"**LLM sampling temperature** is: '{st.session_state._chatbot.temperature}'",
        )
    )


def _reset(request: str):
    st.session_state._chatbot.clear()
    st.session_state._chat.clear()
    st.session_state._chat.append_all(
        Message.from_command(request, f"{welcome} (new session)")
    )


_handlers: dict[str, Callable[[str], None]] = {
    "/c": _connect_server,
    "/h": _help,
    "/s": _system_prompt,
    "/t": _temperature,
    "/r": _reset,
}


def get_handler(request: str) -> Callable[[str], None]:
    if request is not None:
        for key in _handlers:
            if request.startswith(key):
                return _handlers[key]
    return None
