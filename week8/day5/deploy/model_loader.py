from llama_cpp import Llama
from config import MODEL_PATH, CONTEXT_WINDOW

# Global variable to cache the model in memory
_llm_instance = None

def get_llm():
    """
    Returns the cached LLM instance. If it doesn't exist, it loads it into RAM first.
    """
    global _llm_instance
    
    if _llm_instance is None:
        print(f"\n[SYSTEM] Loading AI Model into RAM from: {MODEL_PATH}")
        print("[SYSTEM] This will only happen once...")
        
        _llm_instance = Llama(
            model_path=MODEL_PATH,
            n_ctx=CONTEXT_WINDOW,
            verbose=False  # Keeps the API terminal logs clean
        )
        print("[SYSTEM] Model cached and ready for inference!\n")
        
    return _llm_instance