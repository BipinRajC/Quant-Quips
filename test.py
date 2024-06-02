import requests
import re
import json
from datetime import datetime, timedelta

class ChatBot():
    def __init__(self):
        self.endpoint = "https://https.extension.phind.com/agent/"
        self.system_prompt = "You are a algotrading helper. Provide insights on the strategies and code given and help to make it accurate"
        self.model = "Phind Instant"
    
    def generate_response(self, prompt: list, user_system_prompt: str = None, model: str = "Phind Instant", stream_chunk_size: int = 12, stream: bool = True) -> str:
        if user_system_prompt:
            self.system_prompt = user_system_prompt
        headers = {"User-Agent": ""}
        
        # Insert the system prompt at the beginning of the conversation history
        prompt.insert(0, {"content": self.system_prompt, "role": "system"})
        payload = {
            "additional_extension_context": "",
            "allow_magic_buttons": True,
            "is_vscode_extension": True,
            "message_history": prompt,
            "requested_model": model,
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
                    if stream: print(json_modified_value["choices"][0]["delta"]["content"], end="")
                    streaming_text += json_modified_value["choices"][0]["delta"]["content"]
                except: continue

        return streaming_text

class Chain(ChatBot):
    def __init__(self):
        super().__init__()
        self.prompt_history = []
        self.context_hierarchy = {}  # Key: hierarchy level, Value: list of contexts
    
    def add_context(self, prompt, role, context, hierarchy_level=None):
        context_dict = {'content': context, 'role': role, 'timestamp': datetime.now()}  # Store context as a dictionary
        if hierarchy_level is not None:
            if hierarchy_level not in self.context_hierarchy:
                self.context_hierarchy[hierarchy_level] = []
            self.context_hierarchy[hierarchy_level].append(context_dict)
        else:
            prompt.append(context_dict)
        self.prompt_history.append(prompt)
        print(f"Added context: {context} with role {role}. Current prompt history:\n{self.prompt_history}")
    
    def prune_context(self, threshold):
        current_time = datetime.now()
        for hierarchy_level, contexts in self.context_hierarchy.items():
            pruned_contexts = [context for context in contexts if (current_time - context['timestamp']) < threshold]
            self.context_hierarchy[hierarchy_level] = pruned_contexts
            print(f"Pruned contexts for hierarchy level {hierarchy_level}: {pruned_contexts}")

# Example usage
if __name__ == "__main__":
    prompt = [
        {"content": "My name is Sreejan.", "role": "user"},
        {"content": "Nice to meet you, Sreejan.", "role": "assistant"},
        {"content": "What is my name", "role": "user"},
    ]
    responseGen = Chain()

    # Adding context with hierarchy
    responseGen.add_context(prompt, "assistant", "This is a reminder about our previous conversation.", hierarchy_level=1)
    responseGen.add_context(prompt, "user", "Can you remind me what we talked about?", hierarchy_level=1)

    # Simulate generating a response
    api_response = "This was about discussing names."
    responseGen.add_context(prompt, "assistant", api_response)

    # Prune context after a certain threshold (e.g., 5 minutes)
    responseGen.prune_context(threshold=timedelta(minutes=5))

    # Continue with your logic to interact with the AI model...
