import os
import chromadb
from dotenv import load_dotenv

def test_chroma_cloud():
    # Load environment variables
    load_dotenv()
    
    host = os.getenv("CHROMA_CLOUD_HOST", "").strip()
    api_key = os.getenv("CHROMA_API_KEY", "").strip()
    tenant = os.getenv("CHROMA_TENANT", "").strip()
    database = os.getenv("CHROMA_DATABASE", "").strip()
    
    print(f"Connecting to Chroma Cloud at: '{host}'")
    print(f"Tenant: '{tenant}'")
    print(f"Database: '{database}'")
    print(f"API Key Length: {len(api_key)}")
    
    try:
        # Initialize HttpClient with correct header for Chroma Cloud
        client = chromadb.HttpClient(
            host=f"https://{host}",
            tenant=tenant,
            database=database,
            headers={"x-chroma-token": api_key}
        )
        
        # Try a heartbeat
        heartbeat = client.heartbeat()
        print(f"Heartbeat successful: {heartbeat}")
        
        # List collections
        collections = client.list_collections()
        print(f"\nCollections found: {len(collections)}")
        for col in collections:
            print(f"- {col.name}")
            
        print("\nSUCCESS: Connected to Chroma Cloud successfully!")
        
    except Exception as e:
        print(f"\nFAILURE: Could not connect to Chroma Cloud.")
        print(f"Error details: {str(e)}")

if __name__ == "__main__":
    test_chroma_cloud()
