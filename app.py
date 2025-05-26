import logging
import sys

import streamlit as st

from chat import Chat
from chatbot import ChatBot
from defaults import connection_alert, title, welcome
from handlers import get_handler
from message import Message

logger = logging.getLogger("chatbot")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)


st.set_page_config(initial_sidebar_state="collapsed")
st.title(title)


if "_chatbot" not in st.session_state:
    st.session_state._chatbot = ChatBot()
if "_chat" not in st.session_state:
    st.session_state._chat = Chat()
    st.session_state._chat.append(Message.from_app_message(welcome))


for message in st.session_state._chat._history:
    with st.chat_message(message.role):
        st.markdown(message.to_markdown())

if prompt := st.chat_input("What's up? (type /h for help)", key="_chat_input"):
    prompt = prompt.strip()
    handler = get_handler(prompt)
    if handler is not None:
        handler(prompt)
        st.rerun()
    else:
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state._chat.append(Message.from_user_message(prompt))
        try:
            stream = st.session_state._chatbot.send_user_request(prompt)
            if stream is None:
                message = st.session_state._chat.append(
                    Message()
                    .from_app_message(f"{connection_alert}")
                    .with_warning_severity()
                )
                with st.chat_message(message.role):
                    st.markdown(message.to_markdown())
            else:
                with st.chat_message("assistant"):
                    response = st.write_stream(stream)
                    logger.info(f"response is {response}")
                    response_message = Message.from_response(response=response)
                    st.session_state._chatbot.append(response_message)
                    st.session_state._chat.append(response_message)
        except Exception as error:
            logger.error("An error occurred while interacting with LLM", exc_info=True)
            error_message = Message.from_response(
                response="Cannot interact with LLM", error=error
            )
            st.session_state._chatbot.append(error_message)
            st.session_state._chat.append(error_message)
            st.rerun()


with st.sidebar:
    try:
        llm_model = st.session_state._chatbot.connected_model()
        if llm_model is not None:
            with st.expander(
                f"✅ Connected to LLM at {st.session_state._chatbot.host}."
            ):
                st.markdown(f"**LLM model**: {llm_model}")
                st.markdown(f"**Temperature**: {st.session_state._chatbot.temperature}")
                st.markdown(
                    f"**System prompt**: {st.session_state._chatbot.system_prompt}"
                )
        else:
            st.error("Please configure a valid LLM server host", icon="⚠️")
    except Exception as error:
        st.error(
            f"Cannot fetch LLM details from {st.session_state._chatbot.host}: `{str(error)}`",
            icon="⚠️",
        )

    cols = st.columns([5, 1, 1])
    with cols[0]:
        st.markdown("**Message History**")
    with cols[2]:
        if st.button(
            "",
            type="tertiary",
            key="del-all",
            icon=":material/delete:",
            help="Delete all items from history",
        ):
            st.session_state._chat.delete_history()
            st.rerun()
    for idx, message in enumerate(st.session_state._chat.history_messages()):
        cols = st.columns([5, 1, 1])
        with cols[0]:
            truncated = message.content.strip()
            if len(truncated) > 30:
                truncated = f"{truncated[:30]}..."
            st.write(truncated)
        with cols[1]:
            if st.button(
                "",
                type="tertiary",
                key=f"copy-{idx}",
                icon=":material/content_copy:",
                help="Copy text to clipboard",
            ):
                import clipboard

                clipboard.copy(message.content)
        with cols[2]:
            if st.button(
                "",
                type="tertiary",
                key=f"del-{idx}",
                icon=":material/delete:",
                help="Delete item from history",
            ):
                st.session_state._chat.delete_from_history(message)
                st.rerun()
