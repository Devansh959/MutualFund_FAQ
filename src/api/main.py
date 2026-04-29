from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import threading
from dotenv import load_dotenv
import google.generativeai as genai
from .query_engine import QueryEngine
from .privacy import PIIScrubber

load_dotenv()

# Configure LLM
model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash-lite")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel(model_name)

app = FastAPI(title="Mutual Fund FAQ Assistant API")
query_engine = QueryEngine()

# Global in-memory store for thread history
HISTORY_STORE = {} # {thread_id: [{"query": str, "answer": str}]}
history_lock = threading.Lock()

class QueryRequest(BaseModel):
    query: str
    thread_id: str = "default"

class QueryResponse(BaseModel):
    answer: str
    source_link: str
    last_updated: str

@app.post("/ask", response_model=QueryResponse)
def ask_question(request: QueryRequest):
    # 1. PII Scrubbing
    request.query = PIIScrubber.scrub(request.query)

    # 2. Intent Classification (Advisory vs Facts)
    advisory_keywords = ["should i buy", "is it good", "recommend", "advice", "suggest", "better", "best", "compare", "pick", "suggest", "portfolio"]
    is_advisory = any(keyword in request.query.lower() for keyword in advisory_keywords)
    
    # 3. Performance Query Detection
    performance_keywords = ["returns", "performance", "yield", "profit", "how much return", "historical"]
    is_performance = any(keyword in request.query.lower() for keyword in performance_keywords)

    if is_advisory:
        return QueryResponse(
            answer="I can only provide factual information about mutual fund schemes. For investment advice or recommendations, please consult a SEBI-registered financial advisor. You can learn more about investor protection and education at AMFI India.",
            source_link="https://www.amfiindia.com/investor-corner",
            last_updated="N/A"
        )
    
    if is_performance:
        # For performance, we provide the source link but refuse to calculate or discuss returns
        return QueryResponse(
            answer="I am not authorized to provide historical performance data or return calculations. Please refer to the official scheme factsheet for the most accurate performance metrics.",
            source_link="https://www.hdfcfund.com/information/factsheets", # Generic HDFC factsheet link
            last_updated="N/A"
        )

    # 4. Retrieve context and history
    history = HISTORY_STORE.get(request.thread_id, [])
    context_items = query_engine.retrieve_context(request.query)
    
    if not context_items:
        return QueryResponse(
            answer="I'm sorry, I couldn't find any factual information regarding your query in our records.",
            source_link="N/A",
            last_updated="N/A"
        )
    
    # 5. Build Prompt with History
    prompt = query_engine.format_prompt(request.query, context_items, history=history)
    
    # 6. Generate Answer
    try:
        response = model.generate_content(prompt)
        raw_answer = response.text.strip()
        
        # 7. Validate and Format
        answer = query_engine.validate_and_format_response(raw_answer, context_items)
        
        # 8. Update History Store
        with history_lock:
            if request.thread_id not in HISTORY_STORE:
                HISTORY_STORE[request.thread_id] = []
            HISTORY_STORE[request.thread_id].append({"query": request.query, "answer": answer})
            HISTORY_STORE[request.thread_id] = HISTORY_STORE[request.thread_id][-5:]

        # 9. Extract Citation and Metadata
        primary_metadata = context_items[0]['metadata']
        source_link = primary_metadata.get('source_url', "Official Groww Portal")
        last_updated = primary_metadata.get('last_updated', "Recently")
        
        return QueryResponse(
            answer=answer,
            source_link=source_link,
            last_updated=last_updated
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Generation Error: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model": model_name, "vector_db": "ChromaDB"}
