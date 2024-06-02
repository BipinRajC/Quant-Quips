import requests
import re
import json

class ChatBot():
    def __init__(self):
        self.endpoint = "https://https.extension.phind.com/agent/"
        self.system_prompt = "You are a algotrading helper. Provide insights on the strategies and code given and help to make it accurate"
        self.model = "Phind Instant"
    
    def generate_response(self, prompt: list,user_system_prompt:str = None, model: str = "Phind Instant", stream_chunk_size: int = 12, stream: bool = True) -> str:
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
        #print(payload)

        # Send POST request and stream response
        response = requests.post(self.endpoint, headers=headers, json=payload, stream=True)
        # Collect streamed text content
        streaming_text = ""
        for value in response.iter_lines(decode_unicode=True, chunk_size=stream_chunk_size):
            modified_value = re.sub("data:", "", value)
            #print(modified_value)
            if modified_value:
                json_modified_value = json.loads(modified_value)
                #print(json_modified_value,"\n")
                try:
                    if stream: print(json_modified_value["choices"][0]["delta"]["content"], end="")
                    streaming_text += json_modified_value["choices"][0]["delta"]["content"]
                except: continue

        return streaming_text


class Chain(ChatBot):
    def __init__(self):
        self.Chatbot = ChatBot()
        self.endpoint = self.Chatbot.endpoint
        self.system_prompt = self.Chatbot.system_prompt
        self.model = self.Chatbot.model
          
    def remove_first(self, prompt):
        print(prompt[1:])
        return prompt[1:]
    
    def add_context(self, prompt, role ,context):
        prompt.insert(len(prompt), { "content": context,"role": role,})
        print(prompt,"\n")
        return prompt
    
    
        







if __name__ == "__main__":
    # Predefined system prompt
    #system_prompt = "Be Helpful and Friendly. Keep your response straightforward, short and concise"
    # system_prompt = "Be Helpful and Friendly. Keep your response straightforward, long and detailed"
    # system_prompt = "Talk like Shakespeare"

    # Predefined conversational history that includes providing a name and then asking the AI to recall it
    prompt = [
        { "content": "My name is Sreejan.","role": "user"},
        { "content": "Nice to meet you, Sreejan.","role": "assistant"},
        {"content": "What is my name","role": "user"},
    ]

    responseGen = Chain()
    
    # Call the generate function with the predefined conversational history
    api_response = responseGen.generate_response(prompt=prompt, model="Phind Instant", stream=False)
    print("\n\nResponse content:", api_response,"\n\n------------\n\n")
    prompt = responseGen.add_context(prompt=prompt,role = "assistant",context=api_response)
    #prompt.insert(len(prompt), {"role": "assistant", "content": api_response})
    prompt = responseGen.add_context(prompt=prompt,role="user",context="What is our previous conversation about ?")
    #prompt.insert(len(prompt), {"role": "user", "content": "What is our previous conversation about ?"})
    #print("\n\n",prompt,"\n\n")
    api_response = responseGen.generate_response(prompt=prompt, model="Phind Instant", stream=False)
    print("\n\nResponse content:", api_response,"\n\n------------\n\n")
    #print("\n\nResponse content:", api_response) 

