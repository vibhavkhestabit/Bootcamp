# IMAGE-RAG (MULTIMODAL RAG)

## 1. CLIP Embeddings (The Multimodal Bridge)

CLIP (Contrastive Language-Image Pre-training) by OpenAI is the absolute backbone of Multimodal RAG. Before CLIP, AI treated text and images as completely separate universes.

CLIP uses a Dual-Encoder Architecture. It has two separate "brains": a Vision Transformer (ViT) to process images, and a Text Transformer to process words.

- Push and Pull: The model takes an image of a dog and the text "a dog." It mathematically "pulls" their vectors closer together in a shared, high-dimensional space. Simultaneously, it mathematically "pushes" the image of the dog away from the text "a cat."
- The Result: Text and images now live on the exact same mathematical map. This is why our search_by_text and search_by_image functions can use the exact same FAISS database. A text query and an image query are just coordinates pointing to the same neighborhood.

## 2. Caption Generation using BLIP

If CLIP already understands images, why do we need BLIP (Bootstrapping Language-Image Pre-training)?

- CLIP is an Encoder only. It can tell we if an image and a text string match, but it is physically incapable of writing a sentence. It cannot generate text.
- BLIP is an Encoder-Decoder. It looks at an image, processes the visual features, and then actively writes a human-readable sentence explaining what it sees.

Pure visual math is sometimes vague. BLIP forces the visual data into explicit, semantic text. When we pass data to an LLM later in the RAG pipeline, the LLM cannot see the FAISS vectors. It needs the BLIP caption to understand the visual context.

## 3. OCR Extraction using Tesseract

Optical Character Recognition (OCR) is our hard-coded ground truth.

Tesseract uses traditional computer vision combined with Long Short-Term Memory neural networks to recognize character patterns line by line.

Dense vectors (CLIP) are terrible at exact keyword matching. If we have an engineering diagram with the serial number RX-782, CLIP will embed the general vibe of an engineering diagram, but it will completely lose the specific serial number. Tesseract extracts that hard text so we can use it as a metadata filter or pass it directly to the LLM for precise Q&A.

## 4. Multimodal Vector DB Design

A Multimodal Vector Database isn't just a pile of numbers; it requires a specific architectural design to serve RAG applications effectively.

1) The Index (FAISS): This only stores the dense float32 vectors (the CLIP embeddings). It is optimized purely for blazing-fast mathematical distance calculations (Cosine Similarity/Inner Product).
2) The Document Store (Pickle/JSON): This stores the payload (Filenames, BLIP Captions, OCR Text).

When a query comes in, FAISS finds the nearest mathematical neighbors (the IDs). The system then uses those IDs to retrieve the rich metadata payload from the Document Store. This payload is what is finally injected into the LLM's prompt.

