import os
import faiss
import pickle
import numpy as np
import sys

sys.path.append(os.path.abspath("src"))
from embeddings.clip_embedder import CLIPEmbedder

DB_PATH = "src/vectorstore/image_faiss"

class ImageSearch:
    def __init__(self):
        self.clip = CLIPEmbedder()
        print("Loading Image Vector DB...")
        self.index = faiss.read_index(os.path.join(DB_PATH, "images_index.faiss"))
        with open(os.path.join(DB_PATH, "metadata.pkl"), "rb") as f:
            self.metadata_store = pickle.load(f)

    def search_by_text(self, query, top_k):
        """Text -> Image Search"""
        print(f"\n Searching for images matching text: '{query}'")
        query_vector = self.clip.embed_text(query)
        return self._search(query_vector, top_k)

    def search_by_image(self, image_path, top_k):
        """Image -> Image Search"""
        print(f"\n Searching for images similar to: '{image_path}'")
        query_vector = self.clip.embed_image(image_path)
        return self._search(query_vector, top_k)

    def _search(self, query_vector, top_k):

        query_np = np.array([query_vector], dtype=np.float32)
        faiss.normalize_L2(query_np) 
        
        distances, indices = self.index.search(query_np, top_k)
        
        results = []
        for idx in indices[0]:
            if idx != -1 and idx < len(self.metadata_store):
                results.append(self.metadata_store[idx])
        return results

if __name__ == "__main__":
    searcher = ImageSearch()
    
    print("\n" + "="*50)
    print("MODE 1: Text → Image")
    print("="*50)
    results_mode_1 = searcher.search_by_text("cat", top_k=3)
    for res in results_mode_1:
        print(f" Best Match File: {res['filename']}")
        print(f"Caption: {res['caption']}")

    print("\n" + "="*50)
    print("MODE 2: Image → Image")
    print("="*50)
    test_image_path = "src/data/images/images (1).jpeg" 
    
    if os.path.exists(test_image_path):
        results_mode_2 = searcher.search_by_image(test_image_path, top_k=3)
        print(f" Images similar to {os.path.basename(test_image_path)}:")
        for res in results_mode_2:
             print(f" - {res['filename']} (Caption: {res['caption']})")
    else:
        print(f" Could not find {test_image_path} to run Mode 2 test.")

    print("\n" + "="*50)
    print("MODE 3: Image → Text Answer (Ready for LLM)")
    print("="*50)
    if os.path.exists(test_image_path):
        results_mode_3 = searcher.search_by_image(test_image_path, top_k=1)
        for res in results_mode_3:
            print(f" Extracted Context for LLM:")
            print(f"System: 'The user uploaded an image. Here is the data extracted from it:'")
            print(f"- Visual Summary: {res['caption']}")
            print(f"- Hardcoded Text (OCR): {res['ocr_text']}")
            print(f"Question: 'What does this image say?'")