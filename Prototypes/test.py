import requests
import re
import json

class ChatBot:
    """
    A class to interact with the Phind Instant API to generate chatbot responses.
    """
    def __init__(self, endpoint: str = "https://https.extension.phind.com/agent/", system_prompt: str = "You are a algotrading helper. Provide insights on the strategies and code given and help to make it accurate. Given some information understand it and answer.", model: str = "Phind Instant"):
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

if __name__ == "__main__":
    # Test conversation history
    test_prompts = [
        {"content": "My name is Sreejan.", "role": "user"},
        {"content": "Nice to meet you, Sreejan.", "role": "assistant"},
        {"content": "What is my name?", "role": "user"},
        {"content": "Your name is Sreejan.", "role": "assistant"},
        {"content": "What can you do?", "role": "user"},
        {"content": "I can help with algorithmic trading strategies.", "role": "assistant"},
        {"content": "Tell me more about algorithmic trading.", "role": "user"},
        {"content": "Algorithmic trading uses algorithms to make trading decisions.", "role": "assistant"},
        {"content": "Can you provide an example?", "role": "user"},
        {"content": "Sure, here's an example of a simple trading algorithm.", "role": "assistant"},
        {"content": "How can I implement this?", "role": "user"},
        {"content": "You can implement it using Python and trading libraries.", "role": "assistant"},
        {"content": "what libraries i can use for this?", "role": "user"}
    ]

    # Initialize the chatbot and chain with a context window size of 5 for testing
    chat_bot = ChatBot()
    response_gen = Chain(chat_bot, context_window_size=5)

    # Run the conversation and manage context window
    prompt = []
    for message in test_prompts:
        prompt = response_gen.add_context(prompt, role=message["role"], context=message["content"])
        prompt = response_gen.manage_context_window(prompt)
        print("\nCurrent conversation history (trimmed):", prompt)

    # Generate response for the last prompt to see the context in action
    api_response = response_gen.chat_bot.generate_response(prompt=prompt, stream=False)
    print("\n\nFinal Response content:", api_response)
