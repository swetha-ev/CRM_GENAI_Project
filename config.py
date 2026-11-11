import os

import streamlit as st
from dotenv import load_dotenv
from streamlit.errors import StreamlitSecretNotFoundError


load_dotenv()


def get_setting(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)
    if value is not None:
        return value

    try:
        return st.secrets.get(name, default)
    except StreamlitSecretNotFoundError:
        return default
