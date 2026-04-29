import os
import json
import chromadb
from chromadb.utils import embedding_functions
from datetime import datetime
import glob
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration from environment
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "mf_faq_collection").strip()
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-base-en-v1.5").strip()

# Chroma Configuration
CHROMA_PATH = os.getenv("CHROMA_PATH", "./data/vector_db").strip()

class VectorStoreManager:
    def __init__(self):
        # Initialize Local Persistent Chroma client
        self.client = chromadb.PersistentClient(path=CHROMA_PATH)
        
        # Use sentence-transformers for embeddings
        self.embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL_NAME
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=self.embedding_func,
            metadata={"hnsw:space": "cosine"}
        )

    def upsert_chunks(self, chunks):
        """
        Implements the 'Purge and Reload' strategy.
        First, it identifies the unique schemes in the new data, 
        deletes their existing entries, and then inserts the new ones.
        """
        if not chunks:
            print("No chunks to embed.")
            return

        # Identify unique schemes in the current batch
        schemes_to_update = list(set([c['metadata']['scheme_name'] for c in chunks]))
        print(f"Updating data for schemes: {schemes_to_update}")

        # 1. Purge existing data for these schemes
        for scheme in schemes_to_update:
            try:
                self.collection.delete(where={"scheme_name": scheme})
                print(f"Purged existing vectors for: {scheme}")
            except Exception as e:
                print(f"No existing data for {scheme} or delete failed: {e}")

        # 2. Prepare data for insertion
        ids = []
        documents = []
        metadatas = []
        
        for i, chunk in enumerate(chunks):
            # Create a unique ID for each chunk
            scheme_id = chunk['metadata']['scheme_name'].replace(" ", "_").lower()
            unique_id = f"{scheme_id}_{chunk['metadata']['chunk_id']}_{datetime.now().strftime('%Y%m%d')}"
            
            ids.append(unique_id)
            documents.append(chunk['content'])
            # Chroma requires metadata values to be str, int, float or bool
            clean_metadata = {k: v for k, v in chunk['metadata'].items() if v is not None}
            metadatas.append(clean_metadata)

        # 3. Insert in batches
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            end = i + batch_size
            self.collection.add(
                ids=ids[i:end],
                documents=documents[i:end],
                metadatas=metadatas[i:end]
            )
            print(f"Inserted batch {i//batch_size + 1} ({len(ids[i:end])} chunks)")

    def process_latest_chunks(self):
        # Find the latest processed chunks file
        list_of_files = glob.glob('data/processed/chunks_*.json')
        if not list_of_files:
            print("No processed chunks found.")
            return
        
        latest_file = max(list_of_files, key=os.path.getctime)
        print(f"Embedding chunks from: {latest_file}")
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
            
        self.upsert_chunks(chunks)
        print("Embedding and Vector DB update complete.")

if __name__ == "__main__":
    manager = VectorStoreManager()
    manager.process_latest_chunks()
