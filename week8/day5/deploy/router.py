import logging
import config
from model_loader import get_llm

logger = logging.getLogger(__name__)

class LocalLLMRouter:
    def __init__(self):
        print("[System] Loading GGUF Model into memory... Please wait.")
        self.llm = get_llm()
        self.system_prompt = {"role": "system", "content": "You are a helpful and smart AI coding assistant."}
        print("[System] Model loaded successfully.")

    def generate(self, prompt, max_tokens, temperature, top_p, top_k, stream):
        """Endpoint 1: Raw Text Generation"""
        if stream:
            def stream_generator():
                stream_obj = self.llm.create_completion(
                    prompt=prompt, max_tokens=max_tokens,
                    temperature=temperature, top_p=top_p, top_k=top_k, stream=True
                )
                for chunk in stream_obj:
                    yield chunk["choices"][0]["text"]
            return stream_generator()
            
        else:
            output = self.llm.create_completion(
                prompt=prompt, max_tokens=max_tokens,
                temperature=temperature, top_p=top_p, top_k=top_k
            )
            return output["choices"][0]["text"].strip()

    def chat(self, ui_messages, max_tokens, temperature, top_p, top_k, stream):
        """Endpoint 2: Stateful Chat Completion"""
        # 1. Prepend the system prompt to the user's conversation history
        full_messages = [self.system_prompt] + ui_messages
        
        # 2. Enforce the Sliding Window (Keep system prompt + last 10 messages)
        if len(full_messages) > 11:
            full_messages = [full_messages[0]] + full_messages[-10:]

        if stream:
            def chat_stream_generator():
                stream_obj = self.llm.create_chat_completion(
                    messages=full_messages, 
                    max_tokens=max_tokens, temperature=temperature, 
                    top_p=top_p, top_k=top_k, stream=True
                )
                for chunk in stream_obj:
                    if "content" in chunk["choices"][0]["delta"]:
                        yield chunk["choices"][0]["delta"]["content"]
            return chat_stream_generator()
            
        else:
            output = self.llm.create_chat_completion(
                messages=full_messages, 
                max_tokens=max_tokens, temperature=temperature, 
                top_p=top_p, top_k=top_k
            )
            return output["choices"][0]["message"]["content"].strip()