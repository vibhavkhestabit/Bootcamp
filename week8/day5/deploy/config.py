import os

# PATH CONFIGURATION
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "quantized", "model-q4_0.gguf")

# MODEL HYPERPARAMETERS (Defaults)
CONTEXT_WINDOW = 2048   # Maximum memory buffer for the AI
MAX_TOKENS = 512        # Default max words to generate
DEFAULT_TEMP = 0.7      # Creativity: 0.0 is robotic, 1.0 is chaotic
DEFAULT_TOP_P = 0.9     # Controls vocabulary diversity
DEFAULT_TOP_K = 40      # Restricts the AI to the top 40 most likely next words