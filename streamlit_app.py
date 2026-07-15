import sys
import time

import streamlit as st
import requests

def sigterm_handler(signum, frame):
    sys.exit(0)

#signal.signal(signal.SIGTERM, sigterm_handler)

def fetch_messages():
    try:
        response = requests.get('http://localhost:5000/get_messages')
        if response.status_code == 200:
            return response.json()["messages"]
        else:
            return []
    except Exception as e:
        st.error(f"Failed to fetch messages: {str(e)}")
        return []

def display_messages(messages):
    for message in messages:
        st.info(message)

def main():
    st.title('Terminal Text Display in Word Bubbles')

    # st.rerun() restarts this whole script, so a plain local list would
    # reset to [] every time and re-print every message as "new". Keep the
    # seen-set in session_state so it survives reruns (no duplicates).
    if "displayed" not in st.session_state:
        st.session_state.displayed = []

    messages = fetch_messages()
    new_messages = [m for m in messages if m not in st.session_state.displayed]
    if new_messages:
        display_messages(new_messages)
        st.session_state.displayed.extend(new_messages)

    time.sleep(1)   # poll once a second instead of busy-looping the server
    st.rerun()

if __name__ == "__main__":
    main()

