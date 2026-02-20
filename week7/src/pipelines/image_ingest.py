import os
import pickle
import faiss
import numpy as np
import pytesseract
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import sys

sys.path.append(os.path.abspath("src"))
from embeddings.clip_embedder import CLIPEmbedder

IMAGE_DIR = "src/data/images"
DB_PATH = "src/vectorstore/image_faiss"

class ImageIngestor:
    def __init__(self):
        self.clip = CLIPEmbedder()
        print("Loading BLIP Captioning Model...")
        self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        self.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

    def generate_caption(self, image):
        inputs = self.blip_processor(image, return_tensors="pt")
        out = self.blip_model.generate(**inputs)
        return self.blip_processor.decode(out[0], skip_special_tokens=True)

    def extract_text(self, image):
        return pytesseract.image_to_string(image).strip()

    def process_directory(self):
        os.makedirs(DB_PATH, exist_ok=True)
        metadata_store = []
        vectors = []

        valid_extensions = ('.png', '.jpg', '.jpeg')
        files = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(valid_extensions)]
        
        if not files:
            print(f"⚠️ No images found in {IMAGE_DIR}. Please add some and try again.")
            return

        for filename in files:
            filepath = os.path.join(IMAGE_DIR, filename)
            image = Image.open(filepath).convert("RGB")
            
            print(f"\nProcessing: {filename}")
            
            # 1. AI Captioning
            caption = self.generate_caption(image)
            print(f" - Caption: {caption}")
            
            # 2. OCR Extraction
            ocr_text = self.extract_text(image)
            if ocr_text:
                print(f" - OCR Found: {len(ocr_text)} characters")
            
            # 3. Embedding
            embedding = self.clip.embed_image(filepath)

            vectors.append(embedding)
            metadata_store.append({
                "filename": filename,
                "filepath": filepath,
                "caption": caption,
                "ocr_text": ocr_text[:200] + "..." if len(ocr_text) > 200 else ocr_text
            })

        # --- THE MATH FIX IS HERE ---
        # 1. Convert to numpy array
        vectors_np = np.array(vectors, dtype=np.float32)
        
        # 2. Normalize lengths to exactly 1.0 (Modifies array in-place)
        faiss.normalize_L2(vectors_np)
        
        # 3. Use Inner Product (Which now equals Cosine Similarity)
        dimension = len(vectors[0])
        index = faiss.IndexFlatIP(dimension) 
        
        # 4. Save to FAISS
        index.add(vectors_np)
        faiss.write_index(index, os.path.join(DB_PATH, "images.index"))
        
        with open(os.path.join(DB_PATH, "metadata.pkl"), "wb") as f:
            pickle.dump(metadata_store, f)
            
        print(f"\n✅ Successfully ingested {len(vectors)} images into Multimodal Vector DB.")

if __name__ == "__main__":
    print("--- Starting Multimodal Ingestion Pipeline ---")
    ingestor = ImageIngestor()
    ingestor.process_directory()