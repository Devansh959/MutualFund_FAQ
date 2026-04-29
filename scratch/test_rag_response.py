import sys
import os
import asyncio
from pydantic import BaseModel

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api.main import ask_question, QueryRequest

async def test_response():
    print("--- Testing RAG Response for Silver ETF ---")
    query = "what is the nav of HDFC Silver ETF FoF Direct Growth"
    request = QueryRequest(query=query)
    
    try:
        response = await ask_question(request)
        print(f"\nQUERY: {query}")
        print("-" * 50)
        print(f"ANSWER: {response.answer}")
        print(f"SOURCE: {response.source_link}")
        print(f"LAST UPDATED: {response.last_updated}")
        print("-" * 50)
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    asyncio.run(test_response())
