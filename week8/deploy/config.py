import os

# ---------------------------------------------------------
# PATH CONFIGURATION
# ---------------------------------------------------------
# This dynamically finds the root 'week8' folder, no matter where you run the script from
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Pointing to the exact GGUF file I see in your VS Code sidebar
MODEL_PATH = os.path.join(BASE_DIR, "quantized", "model-q4_0.gguf")

# ---------------------------------------------------------
# MODEL HYPERPARAMETERS (Defaults)
# ---------------------------------------------------------
CONTEXT_WINDOW = 2048   # Maximum memory buffer for the AI
MAX_TOKENS = 512        # Default max words to generate
DEFAULT_TEMP = 0.7      # Creativity: 0.0 is robotic, 1.0 is chaotic
DEFAULT_TOP_P = 0.9     # Controls vocabulary diversity
DEFAULT_TOP_K = 40      # Restricts the AI to the top 40 most likely next words