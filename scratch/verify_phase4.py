import sys
import os
# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api.query_engine import QueryEngine

def verify_phase4():
    print("--- Initializing Advanced Query Engine ---")
    engine = QueryEngine()
    
    print("\n--- Testing Advanced Hybrid Retrieval (Vector + BM25 + Rerank) ---")
    test_queries = [
        "What is the exit load for HDFC Mid Cap fund?",
        "What is the expense ratio of the silver etf?",
        "Who is the fund manager for HDFC Flexi Cap?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        results = engine.retrieve_context(query)
        
        for i, r in enumerate(results):
            print(f"  Result {i+1} (Rerank Score: {r['rerank_score']:.4f}):")
            print(f"    Scheme: {r['metadata']['scheme_name']}")
            print(f"    Content: {r['content'][:100]}...")

    print("\n--- Verification Complete ---")

if __name__ == "__main__":
    verify_phase4()
