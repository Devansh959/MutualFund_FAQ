import os
from dotenv import load_dotenv

load_dotenv()

print(f"CHROMA_PATH: {os.getenv('CHROMA_PATH')}")
print(f"COLLECTION_NAME: {os.getenv('COLLECTION_NAME')}")
print(f"EMBEDDING_MODEL_NAME: {os.getenv('EMBEDDING_MODEL_NAME')}")
print(f"GOOGLE_API_KEY: {'Set' if os.getenv('GOOGLE_API_KEY') else 'Not Set'}")
