# ADVANCED RETRIEVAL + CONTEXT ENGINEERING

Today we are going to enhance our retrieval techniques and implement it with new features and functions.

## Hybrid Search: BM25 + Embeddings

Vector embeddings (dense retrieval) are amazing at understanding the meaning of a query, but they are notoriously terrible at finding exact matches for things like part numbers, acronyms, or specific names. If you search for ID-9942, an embedding model might return ID-9943 because they are mathematically similar.

Hybrid Search combines two entirely different search engines:

**1. Embeddings (Dense Search - FAISS)**: Finds concepts. It understands that salary and compensation mean the same thing.

**2. BM25 (Sparse Search - Keyword)**: Finds exact words. It uses an algorithm called Term Frequency-Inverse Document Frequency (TF-IDF) to score chunks based on how many times your exact search words appear.

The EnsembleRetriever runs both searches simultaneously, normalizes their scores, and combines them ( Reciprocal Rank Fusion). This gives you the best of both worlds: semantic understanding and exact keyword matching.

## Reranking (Cross-Encoder / Cosine)

Initial retrieval (like FAISS) needs to search millions of documents instantly. To do this, it uses a Bi-Encoder: it converts your query into a vector, and measures the Cosine Similarity (the angle) against the document vectors. It is incredibly fast, but slightly shallow in its understanding.

A Cross-Encoder (Reranker): Instead of comparing two pre-calculated math coordinates, a Cross-Encoder takes the User Query and the Document Chunk and feeds them together into a Transformer neural network.

The AI reads both texts simultaneously, comparing every word in the query to every word in the document, outputting a highly accurate relevance score from 0.0 to 1.0.

Cross-Encoders are very slow and computationally expensive. You cannot run a Cross-Encoder on a million documents. You use the fast FAISS search to get the Top 20, and then use the slow, highly accurate Cross-Encoder to strictly rerank and find the true Top 3.

## Max Marginal Relevance (MMR)

If you ask a vector database for the top 5 chunks about credit limits, it might return 5 chunks from the exact same page of a policy document because they are all mathematically closest to your query. The LLM receives redundant information and misses out on other important context.

The Solution: MMR is an algorithm designed to balance Relevance with Diversity.

Fetch: It first grabs a larger pool of results (e.g., fetch_k = 20).

Select: It picks the absolute most relevant chunk and adds it to the final list.

Penalize: For the next selection, it calculates the relevance to the query, but subtracts points if the chunk is too similar to the one already selected.

Result: You get a final k = 5 list that covers the topic from multiple different angles rather than repeating the same sentence five times.

4. Chunk Deduplication
The Problem: In a complex pipeline, you might end up with identical text chunks. This often happens because:

You are using Chunk Overlap, which inherently duplicates text.

Hybrid search might pull the exact same chunk from the BM25 index and the FAISS index.

The Solution: A programmatic filter (like the one you built in context_builder.py) that uses a Python set() or hashes the text to instantly drop identical strings.

Why it matters: Passing duplicate text to an LLM wastes expensive tokens, slows down generation time, and can confuse the model's attention mechanism.

5. Optimizing the Context Window for LLMs
The Problem: An LLM's "Context Window" is its short-term memory (e.g., 8,000 tokens for older models, up to 1-2 million for newer ones). Just because you can fit 50 document chunks into the prompt doesn't mean you should.

The Solution: Context Engineering.

The "Lost in the Middle" Phenomenon: Research proves that if you stuff an LLM's prompt with too much text, its reasoning degrades. It heavily focuses on the very first chunk and the very last chunk, completely ignoring the middle.

Strict Filtering: This is why we set top_k=3 or 5. We only pass the highest-signal, lowest-noise data.

Formatting: Wrapping the text in clear structural tags like [Source: document.pdf] trains the LLM to cite its answers, vastly reducing hallucinations.