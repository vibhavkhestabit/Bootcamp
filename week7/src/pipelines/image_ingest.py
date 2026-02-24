import os
import pickle
import faiss
import numpy as np
import pytesseract
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from pdf2image import convert_from_path
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
        out = self.blip_model.generate(**inputs, max_new_tokens=50)
        return self.blip_processor.decode(out[0], skip_special_tokens=True)

    def extract_text(self, image):
        return pytesseract.image_to_string(image).strip()

    def _process_single_image(self, filename, filepath, vectors, metadata_store):
        """Helper function to process a single image and append to lists"""
        image = Image.open(filepath).convert("RGB")
        
        print(f"\nProcessing: {filename}")
        
        # 1. AI Captioning
        caption = self.generate_caption(image)
        print(f" - Caption: {caption}")
        
        # 2. OCR Extraction
        ocr_text = self.extract_text(image)
        if ocr_text:
            print(f" - OCR Found: {len(ocr_text)} characters")
        
        # 3. Embedding (HYBRID FUSION)
        image_embedding = np.array(self.clip.embed_image(filepath))
        caption_embedding = np.array(self.clip.embed_text(caption))

        if ocr_text and ocr_text.strip():
            ocr_embedding = np.array(self.clip.embed_text(ocr_text))
            
            hybrid_embedding = (0.4 * caption_embedding) + (0.3 * ocr_embedding) + (0.3 * image_embedding)
            print(f" Generated 3-way hybrid embedding for {filepath}")
            
        else:
            hybrid_embedding = (0.6 * caption_embedding) + (0.4 * image_embedding)
            print(f" No OCR found. Generated 2-way hybrid embedding for {filepath}")

        vectors.append(hybrid_embedding)

        metadata_store.append({
            "filename": filename,
            "filepath": filepath,
            "caption": caption,
            "ocr_text": ocr_text[:200] + "..." if len(ocr_text) > 200 else ocr_text
        })

    def process_directory(self):
        os.makedirs(DB_PATH, exist_ok=True)
        metadata_store = []
        vectors = []

        valid_extensions = ('.png', '.jpg', '.jpeg', '.pdf')
        files = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(valid_extensions)]
        
        if not files:
            print(f"No images or PDFs found in {IMAGE_DIR}. Please add some and try again.")
            return

        for filename in files:
            filepath = os.path.join(IMAGE_DIR, filename)
            
            if filename.lower().endswith('.pdf'):
                print(f"\nExtracting pages from PDF: {filename}")
                
                pages = convert_from_path(filepath)
                
                for i, page_image in enumerate(pages):
                    page_filename = f"{os.path.splitext(filename)[0]}_page_{i+1}.jpg"
                    page_filepath = os.path.join(IMAGE_DIR, page_filename)
                    
                    page_image.save(page_filepath, 'JPEG')
                    print(f"  -> Extracted {page_filename}")
                    
                    # Process the newly extracted page as a normal image
                    self._process_single_image(page_filename, page_filepath, vectors, metadata_store)
                    
            else:
                self._process_single_image(filename, filepath, vectors, metadata_store)

        # 1. Convert to numpy array
        vectors_np = np.array(vectors, dtype=np.float32)
        
        # 2. Normalize lengths to exactly 1.0
        faiss.normalize_L2(vectors_np)
        
        # 3. Use Inner Product
        dimension = len(vectors[0])
        index = faiss.IndexFlatIP(dimension) 
        
        # 4. Save to FAISS
        index.add(vectors_np)
        faiss.write_index(index, os.path.join(DB_PATH, "images_index.faiss"))
        
        with open(os.path.join(DB_PATH, "metadata.pkl"), "wb") as f:
            pickle.dump(metadata_store, f)
            
        print(f"\nSuccessfully ingested {len(vectors)} items into Multimodal Vector DB.")

if __name__ == "__main__":
    print("--- Starting Multimodal Ingestion Pipeline ---")
    ingestor = ImageIngestor()
    ingestor.process_directory()