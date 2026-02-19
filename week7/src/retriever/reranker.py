from sentence_transformers import CrossEncoder

class DocumentReranker:
    def __init__(self, model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """Initializes the CrossEncoder model."""
        print(f"Loading Reranker Model: {model_name}...")
        self.model = CrossEncoder(model_name)

    def rerank(self, query, documents, top_k=5):
        """Scores and sorts documents based on true semantic relevance."""
        if not documents:
            return []

        pairs = [[query, doc.page_content] for doc in documents]
        scores = self.model.predict(pairs)
        
        scored_docs = list(zip(documents, scores))
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        return [doc for doc, score in scored_docs[:top_k]]