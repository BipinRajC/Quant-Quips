import requests
import re
import json




class ChatBot():
    def __init__(self):
        self.endpoint = "https://https.extension.phind.com/agent/"
        self.system_prompt = "You are a knowledgeable financial advisor. Provide insights on the stock market. Be truthful and accurate."
        
    
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
        print(payload)

        # Send POST request and stream response
        response = requests.post(self.endpoint, headers=headers, json=payload, stream=True)
        # Collect streamed text content
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










if __name__ == "__main__":
    # Predefined system prompt
    #system_prompt = "Be Helpful and Friendly. Keep your response straightforward, short and concise"
    # system_prompt = "Be Helpful and Friendly. Keep your response straightforward, long and detailed"
    # system_prompt = "Talk like Shakespeare"

    # Predefined conversational history that includes providing a name and then asking the AI to recall it
    prompt = [
        {"role": "user", "content": "My name is Sreejan."},
        {"role": "assistant", "content": "Nice to meet you, Sreejan."},
        {"role": "user", "content": "What is my name"},
    ]

    responseGen = ChatBot()
    
    # Call the generate function with the predefined conversational history
    api_response = responseGen.generate_response(prompt=prompt, model="Phind Instant", stream=False)
    print("\n\nResponse content:", api_response,"\n\n------------\n\n")
    prompt.insert(len(prompt), {"role": "assistant", "content": api_response})
    prompt.insert(len(prompt), {"role": "user", "content": "Create Embeddings for this text - Alpha is first greek letter, Beta is second greek letter, Gamma is third greek letter"})
    print("\n\n",prompt,"\n\n")
    api_response = responseGen.generate_response(prompt=prompt, model="Phind Instant", stream=False)
    print("\n\nResponse content:", api_response,"\n\n------------\n\n")
    #print("\n\nResponse content:", api_response) 

