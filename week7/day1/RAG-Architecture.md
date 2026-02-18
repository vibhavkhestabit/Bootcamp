1. RAG Architecture: The "Open Book" Exam
Retrieval-Augmented Generation (RAG) is designed to solve two LLM problems: Knowledge Cutoffs (LLMs don't know what happened yesterday) and Hallucinations (LLMs make things up when they don't know the answer).

The Retriever (The Librarian): Its only job is to search your private data and find the most relevant "pages" or chunks based on a query.

The Generator (The Student): It takes those specific chunks and the user's question to write a coherent answer.

Think of it as an open-book exam. The student (Generator) is smart but hasn't memorized your specific files. The Librarian (Retriever) hands them the correct textbook open to the right page so the student can answer accurately.

2. Chunking Strategies: Size vs. Context
Computers cannot process an entire 100-page PDF at once due to Context Window limits. We must "chunk" the data.

Chunk Size (The Scope): You used 500 characters. If a chunk is too small, it loses the core meaning (e.g., a sentence fragment). If it's too large, the embedding becomes "diluted" because it's trying to represent too many different topics at once.

Overlap (The Safety Net): You used 50 characters. This ensures that if a vital piece of info is split between two chunks, the semantic meaning is preserved in both. Without overlap, a sentence like "The password is... [BREAK] ...12345" would result in two useless chunks.

3. Embedding Pipelines: Turning Language into Math
Computers don't understand words; they understand vectors (lists of numbers).

The Model: all-MiniLM-L6-v2 is a Sentence Transformer. It has been trained on billions of sentences to understand that "automobile" and "car" should sit very close to each other in a mathematical grid.

The Vector: When you ran embedder.py, you converted your text into a 384-dimensional vector. This means every chunk is now a single dot in a 384-dimensional space. "Semantic search" is simply finding which dots are closest to the "dot" created by the user's query.

4. Metadata Tagging: The "Identity Card"
In an enterprise system, raw text isn't enough. You added source, page, and category.

Traceability: It allows the system to say, "I found this in file.pdf on Page 91."

Filtering: In the future, you can tell the retriever, "Only search documents where category == 'Legal'." This makes retrieval much faster and more accurate.

5. Vector Index Structures: How to Search Fast
Searching through 1,000 chunks is easy. Searching through 10,000,000 is hard. FAISS uses specific structures to handle this:

Flat Index: This is what you are likely using now. It is an "Exhaustive Search." It compares the query vector to every single vector in the database. It is 100% accurate but slow for huge data.

IVF (Inverted File Index): It clusters the vectors into "neighborhoods." The search first finds the right neighborhood and then only searches within it.

HNSW (Hierarchical Navigable Small Worlds): This is the current "Gold Standard." It creates a multi-layered graph where the search starts at the top (broad jumps) and zooms in to the bottom (fine-grained matches), much like how a GPS zooms from a country view down to a street view.

6. Mandatory Folder Structure: Why This Way?
You'll notice the structure separates Data from Logic:

pipelines/: Where the "work" happens (moving data from A to B).

vectorstore/: The "Database" (where the math lives).

embeddings/: The "Translator" (independent of the database).

retriever/: The "Search Logic."

This modularity allows you to swap your embedding model in embeddings/ without breaking your search logic in retriever/.

Final Day 1 Deliverable: RAG-ARCHITECTURE.md
To wrap up your core learning, create this file in your root folder.

Markdown

# Local RAG System Architecture - Day 1

## Data Flow
1. **Ingestion**: Raw PDFs are loaded from `data/raw`.
2. **Processing**: Text is cleaned and split using `RecursiveCharacterTextSplitter`.
3. **Enrichment**: Each chunk is tagged with `source`, `page`, and `timestamp`.
4. **Embedding**: `all-MiniLM-L6-v2` converts text chunks into 384-D vectors.
5. **Storage**: Vectors are indexed in a local **FAISS (FlatL2)** store.

## Technical Choices
- **Chunk Size**: 500 tokens (Optimal for MiniLM context window).
- **Overlap**: 50 tokens (Prevents loss of semantic context at boundaries).
- **Index**: FAISS FlatL2 (Chosen for high accuracy on small-to-medium datasets).