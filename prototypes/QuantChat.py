import requests
import re
import json
import streamlit as st 

class ChatBot:
    """
    A class to interact with the Phind Instant API to generate chatbot responses.
    """
    def __init__(self, endpoint: str = "https://https.extension.phind.com/agent/", system_prompt: str = "You are a algotrading helper. Provide insights on the strategies and code given and help to make it accurate", model: str = "Phind Instant"):
        self.endpoint = endpoint
        self.system_prompt = system_prompt
        self.model = model

    def generate_response(self, prompt: list, user_system_prompt: str = None, model: str = None, stream_chunk_size: int = 12, stream: bool = True) -> str:
        """
        Generate a response from the chatbot based on the prompt.

        Parameters:
        - prompt (list): The conversation history as a list of dictionaries.
        - user_system_prompt (str): Custom system prompt if provided.
        - model (str): The model to be used for generating responses.
        - stream_chunk_size (int): The chunk size for streaming the response.
        - stream (bool): Whether to print the response as it streams.

        Returns:
        - str: The chatbot's response.
        """
        if user_system_prompt:
            self.system_prompt = user_system_prompt
        if model:
            self.model = model
        headers = {"User-Agent": ""}
        # Insert the system prompt at the beginning of the conversation history
        if(prompt[0] !={"content": self.system_prompt, "role": "system"}):
            prompt.insert(0, {"content": self.system_prompt, "role": "system"})
        payload = {
            "additional_extension_context": "",
            "allow_magic_buttons": True,
            "is_vscode_extension": True,
            "message_history": prompt,
            "requested_model": self.model,
            "user_input": prompt[-1]["content"],
        }

        # Send POST request and stream response
        response = requests.post(self.endpoint, headers=headers, json=payload, stream=True)
        streaming_text = ""
        for value in response.iter_lines(decode_unicode=True, chunk_size=stream_chunk_size):
            modified_value = re.sub("data:", "", value)
            if modified_value:
                json_modified_value = json.loads(modified_value)
                try:
                    if stream:
                        print(json_modified_value["choices"][0]["delta"]["content"], end="")
                    streaming_text += json_modified_value["choices"][0]["delta"]["content"]
                except:
                    continue

        return streaming_text

class Chain:
    """
    A class to manage conversation chains with the ChatBot.
    """
    def __init__(self, chat_bot: ChatBot, context_window_size: int = 10):
        self.chat_bot = chat_bot
        self.context_window_size = context_window_size

    def remove_first(self, prompt: list) -> list:
        """
        Remove the first message from the prompt list.

        Parameters:
        - prompt (list): The conversation history as a list of dictionaries.

        Returns:
        - list: The updated conversation history.
        """
        return prompt[1:]

    def add_context(self, prompt: list, role: str, context: str) -> list:
        """
        Add a new message to the conversation history.

        Parameters:
        - prompt (list): The conversation history as a list of dictionaries.
        - role (str): The role of the sender ("user" or "assistant").
        - context (str): The message content.

        Returns:
        - list: The updated conversation history.
        """
        prompt.append({"content": context, "role": role})
        return prompt

    def manage_context_window(self, prompt: list) -> list:
        """
        Ensure the conversation history does not exceed the context window size.

        Parameters:
        - prompt (list): The conversation history as a list of dictionaries.

        Returns:
        - list: The updated conversation history within the context window size.
        """
        while len(prompt) > self.context_window_size:
            prompt = self.remove_first(prompt)
        return prompt




# configuring streamlit page settings
st.set_page_config(
    page_title="Quant Chat",
    page_icon="💬",
    layout="centered"
)

# initialize chat session in streamlit if not already present
if "Qchat_history" not in st.session_state:
    st.session_state.Qchat_history = []
    st.session_state.Qchatbot = ChatBot()
    st.session_state.responseChain = Chain(chat_bot = st.session_state.Qchatbot,context_window_size=5)
    

# streamlit page title
st.title("🤖 QuantPhindBot")

# display chat history
for message in st.session_state.Qchat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
# input field for user's message
user_prompt = st.chat_input("Ask QuantBot...")

if user_prompt:
    # add user's message to chat and display it
    st.chat_message("user").markdown(user_prompt)
    st.session_state.Qchat_history.append({"role": "user", "content": user_prompt})

    # generate response using the generate_response method
    response = st.session_state.responseChain.chat_bot.generate_response(prompt=st.session_state.Qchat_history,stream=False)
    
    st.session_state.Qchat_history.append({"role": "assistant", "content": response})

    # display the response
    with st.chat_message("assistant"):
        st.markdown(response)
