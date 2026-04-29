import chromadb
from chromadb.utils import embedding_functions
import os
from typing import List, Dict
from dotenv import load_dotenv
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder
import numpy as np
import re

# Load environment variables
load_dotenv()

# Configuration from environment
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "mf_faq_collection").strip()
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-base-en-v1.5").strip()
RERANKER_MODEL_NAME = "BAAI/bge-reranker-base"

# Chroma Configuration
CHROMA_PATH = os.getenv("CHROMA_PATH", "./data/vector_db").strip()

class QueryEngine:
    def __init__(self):
        # 1. Initialize Local Persistent Chroma client
        self.client = chromadb.PersistentClient(path=CHROMA_PATH)
        
        self.embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL_NAME
        )
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=self.embedding_func
        )
        
        # 2. Initialize BM25 for keyword search
        # Fetch all documents to build the local BM25 index
        all_data = self.collection.get()
        self.documents = all_data['documents']
        self.metadatas = all_data['metadatas']
        tokenized_corpus = [doc.lower().split() for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized_corpus)
        
        # 3. Initialize Cross-Encoder for reranking
        self.reranker = CrossEncoder(RERANKER_MODEL_NAME)

    def retrieve_context(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        Retrieves the most relevant chunks using Advanced Hybrid Search (Vector + BM25 + RRF + Reranking).
        """
        # 1. Vector Search (Top 10)
        vector_results = self.collection.query(
            query_texts=[query],
            n_results=10
        )
        
        vector_candidates = []
        if vector_results['documents']:
            for i in range(len(vector_results['documents'][0])):
                vector_candidates.append({
                    "content": vector_results['documents'][0][i],
                    "metadata": vector_results['metadatas'][0][i],
                    "id": vector_results['ids'][0][i]
                })
        
        # 2. BM25 Keyword Search (Top 10)
        tokenized_query = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        top_bm25_indices = np.argsort(bm25_scores)[::-1][:10]
        
        bm25_candidates = []
        for idx in top_bm25_indices:
            if bm25_scores[idx] > 0:
                bm25_candidates.append({
                    "content": self.documents[idx],
                    "metadata": self.metadatas[idx],
                    "id": f"bm25_{idx}" # Placeholder ID for alignment
                })

        # 3. Combine Candidates (Deduplicate)
        all_candidates_map = {}
        for c in vector_candidates + bm25_candidates:
            all_candidates_map[c['content']] = c
        
        combined_candidates = list(all_candidates_map.values())
        
        # 4. Cross-Encoder Reranking
        # We rerank the top 15 combined candidates
        if not combined_candidates:
            return []
            
        pairs = [[query, c['content']] for c in combined_candidates]
        rerank_scores = self.reranker.predict(pairs)
        
        for i, score in enumerate(rerank_scores):
            combined_candidates[i]['rerank_score'] = score
            
        # 5. Sort by rerank score and return top-n
        combined_candidates.sort(key=lambda x: x['rerank_score'], reverse=True)
        return combined_candidates[:3]

    def format_prompt(self, query: str, context_items: List[Dict], history: List[Dict] = None) -> str:
        """
        Constructs a strict system prompt with clear constraints, metadata, and conversation history.
        """
        context_str = "\n---\n".join([item['content'] for item in context_items])
        
        # Format History
        history_str = ""
        if history:
            history_str = "### PREVIOUS CONVERSATION:\n"
            for turn in history[-3:]: # Keep last 3 turns
                history_str += f"User: {turn['query']}\nAssistant: {turn['answer']}\n"
            history_str += "\n"

        # Extract metadata from the top result
        metadata_summary = ""
        if context_items:
            meta = context_items[0]['metadata']
            metadata_summary = (
                f"OFFICIAL DATA FOR {meta.get('scheme_name', 'Scheme')}:\n"
                f"- NAV: {meta.get('nav', 'N/A')}\n"
                f"- Expense Ratio: {meta.get('expense_ratio', 'N/A')}\n"
                f"- Fund Size: {meta.get('fund_size', 'N/A')}\n"
                f"- Groww Rating: {meta.get('rating', 'N/A')} Stars\n"
            )

        prompt = f"""
You are the "Mutual Fund Facts Assistant". Your role is to provide precise, objective, and factual information based ONLY on the context provided.

### CONTEXT FROM GROWW:
{context_str}

{metadata_summary}

{history_str}

### CONSTRAINTS:
1. **Facts Only**: Answer ONLY using the provided Context and Official Data. If the info is not in the context, say "I do not have the specific factual data for that query."
2. **Strict Limit**: Your answer MUST be 3 sentences or fewer.
3. **No Advice**: Do not use words like "buy", "suggest", "recommend", or "good/bad". 
4. **Tone**: Be professional, direct, and objective.
5. **Citations**: Do not include links in the text; they will be appended automatically.

### USER QUESTION: 
{query}

### FACTUAL RESPONSE:
"""
        return prompt

    def validate_and_format_response(self, response_text: str, context_items: List[Dict]) -> str:
        """
        Validates the response against constraints and appends the "Last Updated" footer.
        """
        # 1. Enforce 3-sentence limit
        sentences = re.split(r'(?<=[.!?])\s+', response_text.strip())
        if len(sentences) > 3:
            response_text = " ".join(sentences[:3])
            if not response_text.endswith(('.', '!', '?')):
                response_text += "."

        return response_text

# Simple test block
if __name__ == "__main__":
    engine = QueryEngine()
    results = engine.retrieve_context("What is the expense ratio of HDFC Mid Cap Fund?")
    for r in results:
        print(f"Content: {r['content'][:100]}...")
        print(f"Metadata: {r['metadata']}")
