# ADVANCED RAG + MEMORY +EVALUATION (CAPSTONE)

This system is a Production-Ready Multi-Agent Orchestrator. It doesn't just retrieve data; it evaluates its own performance, critiques its own mistakes, and refines its answers before the user ever sees them.

## Core Architecture & Endpoints

1. /ask — The Hybrid Text RAG Intelligence

This is the "Deep Knowledge" engine designed to handle unstructured data (PDFs, documentation, articles). It utilizes a multi-stage retrieval process to ensure high-precision answers.

- The Hybrid Engine: Unlike standard search, this combines Semantic Search (Vector embeddings for meaning) with Keyword Search (BM25 for exact terms). This ensures that if you search for a specific term like "Revenue Report 2024," the system finds the exact document even if the semantic embedding is slightly broader.
- The Processing Layer:
1. Deduplication: Prevents the LLM from processing redundant information, significantly reducing token costs.
2. Reranking: This acts as the "Brain" of the retrieval. It takes the top 10 raw results and uses a cross-encoder model to re-sort them based on how well they actually answer the specific user query.
- Conversational Awareness: The system injects the last 5 messages from the MemoryStore into the prompt. This enables the AI to handle follow-up questions (e.g., "Summarize the first one") by maintaining a consistent context window.

2. /ask-sql (Deterministic Data)

This endpoint is built for "Zero-Hallucination" data retrieval from structured databases. When dealing with numbers, names, and lists, the system prioritizes code over creativity.
- NL-to-SQL Translation: The LLM acts as a database architect. It analyzes the database schema (table structures, constraints, and column types) and translates the user's natural language into a raw SQL query.
- Safety & Execution: The generated SQL is executed against a local SQLite database. If the query fails, the system catches the error and triggers a self-correction loop to rewrite the SQL before returning a result.
- Result Summarization: Instead of returning a raw, unreadable table, a Summarizer Agent takes the database rows and converts them into a human-readable narrative (e.g., "I found 15 customers; the most recent registration was Vernon Kane").

3. /ask-image (Multimodal Vision)

This route bridges the gap between visual assets and natural language conversation, allowing users to "talk" to their image library.

- Multimodal Vector Search: Utilizing CLIP/SigLIP embeddings, the system maps images and text into the same mathematical space. This allows you to find an image of a "dog" even if the filename is DSC_001.jpg.
- Feature Extraction (OCR + Captions):
- Visual Captions: Describes the scene (e.g., "A golden retriever in a park").
- OCR: Reads physical text inside the image (e.g., text on a receipt or a billboard).
- The Writer Agent: Unlike a search engine that just returns a list of files, this route uses an LLM to read the captions and OCR of all $k$ results. It then synthesizes a conversational report explaining exactly what was found and why it matches the query.

4. /history (Memory Audit)

In complex AI systems, managing "state" is critical. This endpoint acts as the System Monitor for the conversational memory stack.
- Sliding Window Logic: To maintain speed and accuracy, the system uses a 5-message sliding window. This prevents "context drift" where the AI becomes confused by old, irrelevant parts of the conversation.
- Memory Auditing: Running /history allows developers to inspect the MemoryStore in real-time. It reveals exactly what the AI "remembers," making it easy to debug why a specific follow-up question was answered in a certain way.
- Log Synchronization: It confirms that the live session is correctly syncing with the CHAT-LOGS.json file, ensuring that metrics like confidence scores are being recorded for every turn.

🧠 Advanced Day 5 Features
🔄 Self-Reflection & Refinement Loops
If the Auditor Agent detects a problem, it doesn't just fail. It triggers a Refinement Loop.

Auditor: Grades the draft answer (0-100).

Trigger: If Score < 80, the Editor Agent is woken up.

Refinement: The Editor writes a "Critique" explaining what was wrong (e.g., "The SQL query missed a case-sensitivity constraint") and provides a "Revised Answer."

🛡️ Hallucination Detection & Faithfulness
We use Constitutional AI principles to ensure the model stays grounded. The Auditor compares the Final Answer against the Raw Context. If the LLM makes up a fact not present in the context, the score drops, and the user is alerted via the system logs.

📝 Production Logging & Human Feedback
Every single interaction is saved to CHAT-LOGS.json with the following enterprise metrics:

Confidence Score: The Auditor's 0-100 grade.

Faithfulness Status: A label (Faithful/Unfaithful) based on the score.

AI Critique: The "thought process" of the correction.

Human Feedback: A direct Positive/Negative rating from the user (y/n).

⚙️ Configuration & Deployment
Model Centralization: All model names are managed via src/config/model.yaml. This allows for instant upgrades (e.g., switching from gemini-2.5-flash to gemini-3.0-pro) without touching Python code.

Environment: Secured via .env for API keys.

Dependencies: langchain, langchain-google-genai, faiss-cpu, pyyaml, pandas.

🏃 How to Run
Ensure model.yaml is in src/config/.

Run python src/deployment/app.py.

Interact via the CLI and provide feedback for each answer to build the evaluation dataset.