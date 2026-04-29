import sys
import os
# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api.query_engine import QueryEngine

def verify_phase2():
    engine = QueryEngine()
    
    print("--- Testing Hybrid Retrieval & Reranking ---")
    query = "What is the exit load for HDFC Mid Cap fund?"
    print(f"Query: {query}")
    results = engine.retrieve_context(query)
    
    for i, r in enumerate(results):
        print(f"\nResult {i+1} (Score: {r['score']:.4f}):")
        print(f"Content: {r['content'][:150]}...")
        print(f"Metadata: {r['metadata']['scheme_name']}")

    print("\n--- Testing Prompt Construction ---")
    prompt = engine.format_prompt(query, results)
    print("System Prompt Preview:")
    print("-" * 30)
    print(prompt[:500] + "...")
    print("-" * 30)

    print("\n--- Testing Intent Classification (Manual simulation) ---")
    advisory_queries = [
        "Should I buy HDFC Mid Cap?",
        "Recommend me a good fund",
        "Which is better: HDFC Mid Cap or Small Cap?"
    ]
    advisory_keywords = ["should i buy", "is it good", "recommend", "advice", "suggest", "better than", "best fund"]
    
    for q in advisory_queries:
        is_advisory = any(kw in q.lower() for kw in advisory_keywords)
        print(f"Query: '{q}' -> Advisory: {is_advisory}")

if __name__ == "__main__":
    verify_phase2()
