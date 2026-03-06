import time
import torch
import gc
import os
import csv
import json
import random
import psutil
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from llama_cpp import Llama

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
BASE_MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
ADAPTER_PATH = "./adapters"           
GGUF_MODEL = "./quantized/model-q4_0.gguf" 
VAL_FILE = "./data/val.jsonl"  
CSV_PATH = "./benchmarks/results.csv"
NUM_TEST_SAMPLES = 3

benchmark_results = []

# =========================================================
# PART 1: QUANTITATIVE METRICS PIPELINE
# =========================================================

def load_eval_prompts(filepath, n=3):
    """Loads and formats Alpaca prompts from val.jsonl"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    selected_lines = random.sample(lines, min(n, len(lines)))
    samples = []
    
    for line in selected_lines:
        data = json.loads(line)
        inst = data.get("instruction", "")
        inp = data.get("input", "")
        ref = data.get("output", "")
        
        if inp.strip():
            prompt = f"### Instruction:\n{inst}\n\n### Input:\n{inp}\n\n### Response:\n"
        else:
            prompt = f"### Instruction:\n{inst}\n\n### Response:\n"
            
        samples.append({
            "prompt": prompt, 
            "reference": ref,
            "instruction": inst,
            "input": inp
        })
    return samples

def get_vram_mb():
    if torch.cuda.is_available(): return round(torch.cuda.memory_allocated() / (1024 ** 2), 2)
    return 0.0 

def get_ram_mb():
    """✅ NEW: Measures System RAM Usage for this specific Python process"""
    process = psutil.Process(os.getpid())
    return round(process.memory_info().rss / (1024 ** 2), 2)

def calculate_word_f1(prediction, reference):
    """Calculates word-overlap F1 score for accuracy"""
    pred_words = set(prediction.lower().split())
    ref_words = set(reference.lower().split())
    if not pred_words or not ref_words: return 0.0
    
    common = pred_words.intersection(ref_words)
    if not common: return 0.0
    
    precision = len(common) / len(pred_words)
    recall = len(common) / len(ref_words)
    f1 = 2 * (precision * recall) / (precision + recall)
    return round(f1 * 100, 1)

def run_hf_metrics(model_name, model, tokenizer, samples):
    print(f"\n{'='*50}\n[Benchmarking {model_name}...]\n{'='*50}")
    total_tokens, total_time, f1_scores = 0, 0, []
    
    for i, s in enumerate(samples):
        inputs = tokenizer(s["prompt"], return_tensors="pt").to("cuda" if torch.cuda.is_available() else "cpu")
        
        start = time.time()
        outputs = model.generate(**inputs, max_new_tokens=40, do_sample=False)
        latency = time.time() - start
        
        total_time += latency
        total_tokens += (outputs.shape[1] - inputs["input_ids"].shape[1])
        
        response = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()
        score = calculate_word_f1(response, s["reference"])
        f1_scores.append(score)
        
        print(f"\n--- Sample {i+1} ---")
        print(f"Question  : {s['instruction']} {s['input']}".strip())
        print(f"Reference : {s['reference']}")
        print(f"Prediction: {response}")
        print(f"F1 Score  : {score}%")
        
    speed = round(total_tokens / total_time, 2)
    avg_latency = round(total_time / len(samples), 2)
    avg_accuracy = round(sum(f1_scores) / len(f1_scores), 1)
    vram = get_vram_mb()
    ram = get_ram_mb() # <--- NEW: Capture RAM here
    
    # Updated to include RAM in the dictionary
    benchmark_results.append({"Model": model_name, "Tokens/sec": speed, "Latency (s)": avg_latency, "VRAM (MB)": vram, "RAM (MB)": ram, "Accuracy (%)": avg_accuracy})
    print(f"\n✅ FINAL {model_name} -> Speed: {speed} T/s | Latency: {avg_latency}s | VRAM: {vram} MB | RAM: {ram} MB | Accuracy: {avg_accuracy}%")

def run_gguf_metrics(model_name, llm, samples):
    print(f"\n{'='*50}\n[Benchmarking {model_name}...]\n{'='*50}")
    total_tokens, total_time, f1_scores = 0, 0, []
    
    for i, s in enumerate(samples):
        start = time.time()
        output = llm(s["prompt"], max_tokens=40, echo=False)
        latency = time.time() - start
        
        total_time += latency
        total_tokens += output["usage"]["completion_tokens"]
        
        response = output["choices"][0]["text"].strip()
        score = calculate_word_f1(response, s["reference"])
        f1_scores.append(score)
        
        print(f"\n--- Sample {i+1} ---")
        print(f"Question  : {s['instruction']} {s['input']}".strip())
        print(f"Reference : {s['reference']}")
        print(f"Prediction: {response}")
        print(f"F1 Score  : {score}%")
        
    speed = round(total_tokens / total_time, 2)
    avg_latency = round(total_time / len(samples), 2)
    avg_accuracy = round(sum(f1_scores) / len(f1_scores), 1)
    vram = get_vram_mb() 
    ram = get_ram_mb() 
    
    # Updated to include RAM in the dictionary
    benchmark_results.append({"Model": model_name, "Tokens/sec": speed, "Latency (s)": avg_latency, "VRAM (MB)": vram, "RAM (MB)": ram, "Accuracy (%)": avg_accuracy})
    print(f"\n✅ FINAL {model_name} -> Speed: {speed} T/s | Latency: {avg_latency}s | VRAM: {vram} MB | RAM: {ram} MB | Accuracy: {avg_accuracy}%")


# =========================================================
# PART 2: QUALITATIVE GGUF DEMOS
# =========================================================

def streaming_output(llm):
    print("\n===== 1. Streaming Output Mode =====")
    messages = [
        {"role": "system", "content": "You are a helpful AI coding assistant."},
        {"role": "user", "content": "Explain Artificial Intelligence in simple terms."}
    ]
    stream = llm.create_chat_completion(messages=messages, max_tokens=100, stream=True)
    print("Response: ", end="", flush=True)
    for chunk in stream:
        if "content" in chunk["choices"][0]["delta"]:
            print(chunk["choices"][0]["delta"]["content"], end="", flush=True)
    print("\n")

def batch_inference(llm):
    print("\n===== 2. Sequential Inference =====")
    prompts = ["What is machine learning?", "Define neural networks.", "What is deep learning?"]
    start = time.time()
    for prompt in prompts:
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": prompt}
        ]
        output = llm.create_chat_completion(messages=messages, max_tokens=100)
        response = output["choices"][0]["message"]["content"].strip()
        print(f"\nPrompt: {prompt}\nResponse: {response}")
    end = time.time()
    print(f"\nBatch Inference Time: {end - start:.2f} seconds")

def multi_prompt_test(llm):
    print("\n===== 3. Multi Prompt Test =====")
    prompts = ["Explain artificial intelligence briefly.", "Explain neural networks briefly.", "Explain deep learning briefly."]
    start = time.time()
    for p in prompts:
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": p}
        ]
        output = llm.create_chat_completion(messages=messages, max_tokens=100, temperature=0.7)
        response = output["choices"][0]["message"]["content"].strip()
        print(f"\nPrompt: {p}\nResponse: {response}")
    end = time.time()
    print(f"\nTotal Time: {end - start:.2f} seconds")


# =========================================================
# MAIN EXECUTION
# =========================================================
if __name__ == "__main__":
    print("Loading Validation Data...")
    samples = load_eval_prompts(VAL_FILE, NUM_TEST_SAMPLES)
    
    # --- 1. Base Model Metrics ---
    tok = AutoTokenizer.from_pretrained(BASE_MODEL_NAME)
    base = AutoModelForCausalLM.from_pretrained(BASE_MODEL_NAME, device_map="auto", dtype=torch.float16)
    run_hf_metrics("Base (FP16)", base, tok, samples)
    del base; gc.collect()
    if torch.cuda.is_available(): torch.cuda.empty_cache()

    # --- 2. Fine-Tuned Model Metrics ---
    base = AutoModelForCausalLM.from_pretrained(BASE_MODEL_NAME, device_map="auto", dtype=torch.float16)
    ft_model = PeftModel.from_pretrained(base, ADAPTER_PATH)
    run_hf_metrics("Fine-Tuned (LoRA)", ft_model, tok, samples)
    del ft_model, base, tok; gc.collect()
    if torch.cuda.is_available(): torch.cuda.empty_cache()

    # --- 3. GGUF Metrics ---
    gguf_llm = Llama(model_path=GGUF_MODEL, n_ctx=2048, verbose=False)
    run_gguf_metrics("GGUF (Q4_0)", gguf_llm, samples)
    
    # --- 4. Save CSV ---
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    with open(CSV_PATH, mode='w', newline='') as file:
        # Added RAM (MB) to the fieldnames list
        writer = csv.DictWriter(file, fieldnames=["Model", "Tokens/sec", "Latency (s)", "VRAM (MB)", "RAM (MB)", "Accuracy (%)"])
        writer.writeheader()
        writer.writerows(benchmark_results)
    print(f"\n✅ Benchmarks complete. Results saved strictly to {CSV_PATH}")
    
    # --- 5. Run User Demos ---
    print("\n" + "="*50 + "\n LAUNCHING GGUF VISUAL DEMOS\n" + "="*50)
    streaming_output(gguf_llm)
    batch_inference(gguf_llm)
    multi_prompt_test(gguf_llm)
    