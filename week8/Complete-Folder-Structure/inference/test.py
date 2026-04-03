
from llama_cpp import Llama
import time

# -------------------------------
# Model Path & Initialization
# -------------------------------
GGUF_MODEL = "./quantized/model-q4_0.gguf" 

# Added n_ctx=2048 to give the AI a bigger memory buffer
# Added verbose=False to hide the massive wall of text logs
llm = Llama(
    model_path=GGUF_MODEL,
    n_ctx=2048, 
    verbose=False 
)

# -------------------------------
# 1. Streaming Output Mode
# -------------------------------
def streaming_output():
    print("\n===== 1. Streaming Output Mode =====")

    # Using the Chat format (System + User)
    messages = [
        {"role": "system", "content": "You are a helpful AI coding assistant."},
        {"role": "user", "content": "Explain Artificial Intelligence in simple terms."}
    ]

    # Switched to create_chat_completion
    stream = llm.create_chat_completion(
        messages=messages,
        max_tokens=100, # Increased so it doesn't cut off
        stream=True
    )

    print("Response: ", end="", flush=True)

    for chunk in stream:
        # The dictionary structure for chat streaming is slightly different
        if "content" in chunk["choices"][0]["delta"]:
            print(chunk["choices"][0]["delta"]["content"], end="", flush=True)

    print("\n")


# -------------------------------
# 2. Sequential Inference (Batching)
# -------------------------------
def batch_inference():
    print("\n===== 2. Sequential Inference =====")

    prompts = [
        "What is machine learning?",
        "Define neural networks.",
        "What is deep learning?"
    ]

    start = time.time()

    for prompt in prompts:
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": prompt}
        ]
        
        output = llm.create_chat_completion(
            messages=messages,
            max_tokens=100
        )
        
        # Extracting the text from the chat completion dictionary
        response = output["choices"][0]["message"]["content"].strip()

        print(f"\nPrompt: {prompt}")
        print(f"Response: {response}")

    end = time.time()

    print(f"\nBatch Inference Time: {end - start:.2f} seconds")


# -------------------------------
# 3. Multi Prompt Test
# -------------------------------
def multi_prompt_test():
    print("\n===== 3. Multi Prompt Test =====")

    prompts = [
        "Explain artificial intelligence briefly.",
        "Explain neural networks briefly.",
        "Explain deep learning briefly."
    ]

    start = time.time()

    for p in prompts:
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": p}
        ]
        
        output = llm.create_chat_completion(
            messages=messages,
            max_tokens=100,
            temperature=0.7
            # Removed the buggy stop parameters! The chat format handles stops automatically.
        )

        response = output["choices"][0]["message"]["content"].strip()

        print(f"\nPrompt: {p}")
        print(f"Response: {response}")

    end = time.time()

    print(f"\nTotal Time: {end - start:.2f} seconds")


# -------------------------------
# Run All Tests
# -------------------------------
if __name__ == "__main__":
    streaming_output()
    batch_inference()
    multi_prompt_test()
