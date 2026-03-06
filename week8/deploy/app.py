import uuid
import logging
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional

# Import our custom files
import config
from model_loader import get_llm

# ---------------------------------------------------------
# LOGGING SETUP
# ---------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | [%(levelname)s] | RequestID: %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="Local LLM API", description="Day 5 Capstone: GGUF Microservice")

# ---------------------------------------------------------
# PYDANTIC SCHEMAS (Data Validation & Controls)
# ---------------------------------------------------------
class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: int = Field(default=config.MAX_TOKENS)
    temperature: float = Field(default=config.DEFAULT_TEMP)
    top_p: float = Field(default=config.DEFAULT_TOP_P)
    top_k: int = Field(default=config.DEFAULT_TOP_K)
    stream: bool = Field(default=False)

class ChatMessage(BaseModel):
    role: str # 'system', 'user', or 'assistant'
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    max_tokens: int = Field(default=config.MAX_TOKENS)
    temperature: float = Field(default=config.DEFAULT_TEMP)
    top_p: float = Field(default=config.DEFAULT_TOP_P)
    top_k: int = Field(default=config.DEFAULT_TOP_K)
    stream: bool = Field(default=False)

# ---------------------------------------------------------
# ENDPOINT 1: POST /generate (Raw Text Completion)
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# ENDPOINT 2: POST /chat (Infinite Chat & RAG Ready)
# ---------------------------------------------------------
@app.post("/chat")
async def chat_text(req: ChatRequest):
    req_id = str(uuid.uuid4())[:8]
    logger.info(f"{req_id} | POST /chat | Messages Count: {len(req.messages)}")
    
    llm = get_llm()
    
    # Convert Pydantic objects to standard dictionaries for llama.cpp
    formatted_messages = [{"role": msg.role, "content": msg.content} for msg in req.messages]

    # Streaming logic
    if req.stream:
        logger.info(f"{req_id} | Starting Streamed Chat")
        
        def chat_stream_generator():
            stream = llm.create_chat_completion(
                messages=formatted_messages, max_tokens=req.max_tokens,
                temperature=req.temperature, top_p=req.top_p, top_k=req.top_k, stream=True
            )
            for chunk in stream:
                if "content" in chunk["choices"][0]["delta"]:
                    yield chunk["choices"][0]["delta"]["content"]
                    
        return StreamingResponse(chat_stream_generator(), media_type="text/plain")

    # Standard (Non-Streaming) logic
    logger.info(f"{req_id} | Starting Standard Chat")
    output = llm.create_chat_completion(
        messages=formatted_messages, max_tokens=req.max_tokens,
        temperature=req.temperature, top_p=req.top_p, top_k=req.top_k
    )
    
    response_text = output["choices"][0]["message"]["content"].strip()
    logger.info(f"{req_id} | Chat Complete")
    
    return {
        "request_id": req_id,
        "response": response_text
    }