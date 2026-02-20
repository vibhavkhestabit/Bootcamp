import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image

class CLIPEmbedder:
    def __init__(self, model_id="openai/clip-vit-base-patch32"):
        print(f"Loading CLIP Model: {model_id}...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = CLIPModel.from_pretrained(model_id).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(model_id)

    def embed_text(self, text):
        """Converts text into a CLIP vector."""
        inputs = self.processor(text=text, return_tensors="pt", padding=True).to(self.device)
        with torch.no_grad():
            embeddings = self.model.get_text_features(**inputs)
        return embeddings.cpu().numpy().tolist()[0]

    def embed_image(self, image_path):
        """Converts an image file into a CLIP vector."""
        image = Image.open(image_path).convert("RGB")
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            embeddings = self.model.get_image_features(**inputs)
        return embeddings.cpu().numpy().tolist()[0]