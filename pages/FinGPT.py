import os
import json

import streamlit as st
import groq

# configuring openai - api key
working_dir = os.path.dirname(os.path.abspath(__file__))
config_data = json.load(open(f"{working_dir}/config.json"))
#print(config_data)
GROQ_API_KEY = config_data["GROQ_API_KEY"]

# configuring streamlit page settings
st.set_page_config(
    page_title="llama3-70b Chat",
    page_icon="💬",
    layout="centered"
)
client  = groq.Groq(api_key=GROQ_API_KEY)
# initialize chat session in streamlit if not already present
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# streamlit page title
st.title("🤖 QuantBot")

# display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# input field for user's message
user_prompt = st.chat_input("Ask QuantBot...")

if user_prompt:
    # add user's message to chat and display it
    st.chat_message("user").markdown(user_prompt)
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})

    # send user's message to GPT-4o and get a response
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": "You are a algotrading helper named QuantBot. Provide insights on the strategies and code given and help to make it accurate"},
            *st.session_state.chat_history
        ],
        temperature=0.0,
        seed=24
    )

    assistant_response = response.choices[0].message.content
    st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})

    # display GPT-4o's response
    with st.chat_message("assistant"):
        st.markdown(assistant_response)
