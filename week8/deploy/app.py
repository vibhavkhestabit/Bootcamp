import uuid
import logging
import sys
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional

# Import our custom files
import config
from model_loader import get_llm

# LOGGING SETUP
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | [%(levelname)s] | RequestID: %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="Local LLM API", description="Day 5 Capstone: GGUF Microservice")

# --- GLOBAL MEMORY BUFFER (Single-Player Mode) ---
global_chat_history = [
    {"role": "system", "content": "You are a helpful and smart AI coding assistant."}
]

# PYDANTIC SCHEMAS (Data Validation & Controls)
class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: int = Field(default=config.MAX_TOKENS)
    temperature: float = Field(default=config.DEFAULT_TEMP)
    top_p: float = Field(default=config.DEFAULT_TOP_P)
    top_k: int = Field(default=config.DEFAULT_TOP_K)
    stream: bool = Field(default=False)

# Updated schema: Now it just takes your single question!
class ChatRequest(BaseModel):
    message: str 
    max_tokens: int = Field(default=config.MAX_TOKENS)
    temperature: float = Field(default=config.DEFAULT_TEMP)
    top_p: float = Field(default=config.DEFAULT_TOP_P)
    top_k: int = Field(default=config.DEFAULT_TOP_K)
    stream: bool = Field(default=False)


# ENDPOINT 1: POST /generate (Raw Text Completion)
@app.post("/generate")
async def generate_text(req: GenerateRequest):
    req_id = str(uuid.uuid4())[:8] # Generate a unique ID for this request
    logger.info(f"{req_id} | POST /generate | Prompt: '{req.prompt[:30]}...'")
    
    llm = get_llm()

    # Streaming logic
    if req.stream:
        logger.info(f"{req_id} | Starting Streamed Generation")
        
        def stream_generator():
            stream = llm.create_completion(
                prompt=req.prompt, max_tokens=req.max_tokens,
                temperature=req.temperature, top_p=req.top_p, top_k=req.top_k, stream=True
            )
            for chunk in stream:
                yield chunk["choices"][0]["text"]
                
        return StreamingResponse(stream_generator(), media_type="text/plain")

    # Standard (Non-Streaming) logic
    logger.info(f"{req_id} | Starting Standard Generation")
    output = llm.create_completion(
        prompt=req.prompt, max_tokens=req.max_tokens,
        temperature=req.temperature, top_p=req.top_p, top_k=req.top_k
    )
    
    response_text = output["choices"][0]["text"].strip()
    logger.info(f"{req_id} | Generation Complete")
    
    return {
        "request_id": req_id,
        "response": response_text
    }


# ENDPOINT 2: POST /chat (Stateful Global Chat)
@app.post("/chat")
async def chat_text(req: ChatRequest):
    global global_chat_history
    req_id = str(uuid.uuid4())[:8]
    logger.info(f"{req_id} | POST /chat | Message: '{req.message[:30]}...'")
    
    llm = get_llm()
    
    # 1. Append the new user message to the global history
    global_chat_history.append({"role": "user", "content": req.message})

    # Streaming logic
    if req.stream:
        logger.info(f"{req_id} | Starting Streamed Chat")
        
        def chat_stream_generator():
            global global_chat_history
            stream = llm.create_chat_completion(
                messages=global_chat_history, 
                max_tokens=req.max_tokens,
                temperature=req.temperature, 
                top_p=req.top_p, 
                top_k=req.top_k, 
                stream=True
            )
            
            assistant_reply = ""
            for chunk in stream:
                if "content" in chunk["choices"][0]["delta"]:
                    text_chunk = chunk["choices"][0]["delta"]["content"]
                    assistant_reply += text_chunk
                    yield text_chunk # Yield to the API client
            
            # 2. Save response and slide window AFTER stream finishes
            global_chat_history.append({"role": "assistant", "content": assistant_reply})
            if len(global_chat_history) > 11:
                global_chat_history = [global_chat_history[0]] + global_chat_history[-10:]
                
        return StreamingResponse(chat_stream_generator(), media_type="text/plain")

    # Standard (Non-Streaming) logic
    logger.info(f"{req_id} | Starting Standard Chat")
    output = llm.create_chat_completion(
        messages=global_chat_history, 
        max_tokens=req.max_tokens,
        temperature=req.temperature, 
        top_p=req.top_p, 
        top_k=req.top_k
    )
    
    response_text = output["choices"][0]["message"]["content"].strip()
    
    # 3. Save the AI's response to the global history
    global_chat_history.append({"role": "assistant", "content": response_text})
    
    # 4. MEMORY MANAGEMENT: The Sliding Window
    if len(global_chat_history) > 11:
        global_chat_history = [global_chat_history[0]] + global_chat_history[-10:]
        
    logger.info(f"{req_id} | Chat Complete")
    
    return {
        "request_id": req_id,
        "response": response_text
    }

if __name__ == "__main__":
    import uvicorn
    # If you run `python app.py` it will start the server automatically
    print("\n" + "="*50)
    print(" LAUNCHING LOCAL LLM API SERVER")
    print("="*50)
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)