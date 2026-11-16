import os
import logging
from typing import List, Dict

from config import settings
from schemas import PolicyQueryRequest, PolicyQueryResponse

logger = logging.getLogger(__name__)

# Sample airline policy documents for vector indexing
SAMPLE_POLICIES = [
    {
        "airline": "Emirates",
        "doc": "Emirates Cabin Baggage Policy: Economy passengers are allowed 1 piece of carry-on baggage weighing up to 7 kg (15 lbs) with dimensions not exceeding 55 x 38 x 20 cm. Checked baggage allowance is typically 23 kg to 35 kg depending on ticket class. Cancellation within 24 hours of booking guarantees a full refund."
    },
    {
        "airline": "Delta Air Lines",
        "doc": "Delta Air Lines Baggage Policy: Standard carry-on bag and one personal item are free of charge with no weight limit for most routes. First checked bag fee is $35 for domestic routes, max 23 kg (50 lbs). Cancellations made 24 hours after purchase on Main Cabin or above yield eCredit without penalty fees."
    },
    {
        "airline": "United Airlines",
        "doc": "United Airlines Policies: Basic Economy permits one small personal item under the seat; full-size carry-on requires Economy or higher. Checked bags cost $35 for the first bag under 23 kg. Flight changes can be made without change fees for most Economy and Premium seats."
    },
    {
        "airline": "British Airways",
        "doc": "British Airways Allowance: All passengers enjoy 1 handbag/laptop bag plus 1 cabin bag (up to 23 kg each). Checked bags must fit 90 x 75 x 43 cm dimensions and weigh up to 23 kg. Full refund available within 24 hours of booking if reserved at least 1 week prior to departure."
    },
    {
        "airline": "Lufthansa",
        "doc": "Lufthansa Luggage & Cancellation: Economy Light includes 1 carry-on item up to 8 kg. Checked luggage is available for an extra fee. Economy Classic includes 1 checked bag up to 23 kg. Rebooking is allowed with fare difference adjustments."
    }
]

class PolicyRAGService:
    """
    RAG engine utilizing FAISS vector index and Sentence Transformers
    to retrieve unstructured airline policy context.
    """
    def __init__(self):
        self.index_path = settings.FAISS_INDEX_PATH
        self.embedding_model = None
        self.vector_store = None
        self._initialize_vector_db()

    def _initialize_vector_db(self):
        """Initializes SentenceTransformers and builds FAISS index."""
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
            from langchain_community.vectorstores import FAISS
            from langchain_core.documents import Document

            logger.info("Initializing HuggingFace Embeddings model...")
            self.embedding_model = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL_NAME)

            # Check if local index already exists
            if os.path.exists(self.index_path):
                logger.info("Loading existing FAISS vector index from disk...")
                self.vector_store = FAISS.load_local(
                    self.index_path, 
                    self.embedding_model, 
                    allow_dangerous_deserialization=True
                )
            else:
                logger.info("Building new FAISS vector index with policy knowledge base...")
                docs = [
                    Document(
                        page_content=item["doc"], 
                        metadata={"airline": item["airline"]}
                    ) 
                    for item in SAMPLE_POLICIES
                ]
                self.vector_store = FAISS.from_documents(docs, self.embedding_model)
                self.vector_store.save_local(self.index_path)
                logger.info(f"FAISS index saved successfully at '{self.index_path}'.")

        except Exception as e:
            logger.warning(f"Vector DB initialization fallback mode activated: {e}")
            self.vector_store = None

    def query_policy(self, request: PolicyQueryRequest) -> PolicyQueryResponse:
        """Searches vector database for relevant airline policies."""
        query_text = f"{request.airline} {request.question}"

        if self.vector_store:
            try:
                results = self.vector_store.similarity_search(query_text, k=2)
                retrieved_texts = [doc.page_content for doc in results]
                combined_context = " ".join(retrieved_texts)
                return PolicyQueryResponse(
                    airline=request.airline,
                    question=request.question,
                    answer=combined_context,
                    source_documents=retrieved_texts
                )
            except Exception as e:
                logger.error(f"Error querying FAISS vector store: {e}")

        # Basic text matching fallback if vector store fails
        matched = [
            p["doc"] for p in SAMPLE_POLICIES 
            if request.airline.lower() in p["airline"].lower()
        ]
        fallback_answer = matched[0] if matched else f"Standard policy rules apply for {request.airline}."

        return PolicyQueryResponse(
            airline=request.airline,
            question=request.question,
            answer=fallback_answer,
            source_documents=[fallback_answer]
        )

# Global Service Singleton
rag_service = PolicyRAGService()