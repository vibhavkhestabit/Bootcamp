from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever

class HybridRetriever:
    def __init__(self, vectorstore, all_documents):
        """Initializes Semantic (FAISS) and Keyword (BM25) retrievers."""
        self.vectorstore = vectorstore
        
        self.bm25_retriever = BM25Retriever.from_documents(all_documents)
        self.bm25_retriever.k = 5 
        
        self.vector_retriever = self.vectorstore.as_retriever(
            search_type="mmr", 
            search_kwargs={'k': 5, 'fetch_k': 20} 
        )
        
        self.ensemble_retriever = EnsembleRetriever(
            retrievers=[self.bm25_retriever, self.vector_retriever],
            weights=[0.5, 0.5]
        )

    def retrieve(self, query, metadata_filters=None):
        """Executes the hybrid search."""
        if metadata_filters:
             self.vector_retriever.search_kwargs['filter'] = metadata_filters
             
        return self.ensemble_retriever.invoke(query)