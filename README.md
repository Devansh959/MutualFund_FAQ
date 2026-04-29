# Mutual Fund FAQ Assistant (Facts-Only Q&A)

A Retrieval-Augmented Generation (RAG) assistant designed to provide factual, verifiable information about HDFC Mutual Fund schemes using Groww as the primary data source.

## Features

- **Advanced Retrieval**: Hybrid search combining Vector Embeddings (ChromaDB) and Keyword search (BM25) with Cross-Encoder reranking.
- **Compliance & Safety**:
    - **PII Scrubber**: Automatically redacts PAN, Aadhaar, Bank Account numbers, Emails, and Phone numbers from queries.
    - **Advisory Refusal**: Detects and refuses investment advice or recommendation queries.
    - **Performance Guardrails**: Redirects historical performance queries to official factsheets instead of generating speculative data.
- **Strict Response Constraints**: Answers are limited to 3 sentences and strictly grounded in official context.
- **Automated Ingestion**: Daily ingestion pipeline via GitHub Actions (scheduled at 9:15 AM IST).

## Tech Stack

- **Backend**: FastAPI (Python)
- **LLM**: Gemini 1.5 Flash
- **Embeddings**: `BAAI/bge-base-en-v1.5`
- **Reranker**: `BAAI/bge-reranker-base`
- **Vector Database**: ChromaDB (Cloud)
- **Search**: BM25 (Rank-BM25)

## Project Structure

```
MF_FAQ/
├── Docs/               # Architecture and Problem Statement
├── src/
│   ├── api/            # FastAPI Backend, Query Engine, Privacy logic
│   └── ingestion/      # Scraper, Processor, Embedder
├── tests/              # Unit and Integration tests
├── data/               # Processed chunks and metadata
├── .github/workflows/  # Ingestion scheduler
└── README.md
```

## Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone <repo-url>
   cd MF_FAQ
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-asyncio httpx
   ```

3. **Configure Environment**:
   Create a `.env` file based on `.env.example`:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key
   CHROMA_PATH=./data/vector_db
   COLLECTION_NAME=mf_faq_collection
   ```

4. **Run the Ingestion (Optional)**:
   ```bash
   python src/ingestion/scraper.py
   python src/ingestion/processor.py
   python src/ingestion/embedder.py
   ```

5. **Run the API (Backend)**:
   ```bash
   uvicorn src.api.main:app --reload
   ```

6. **Run the UI (Frontend)**:
   In a new terminal:
   ```bash
   streamlit run app.py
   ```

7. **Run Tests**:
   ```bash
   $env:PYTHONPATH = "."; pytest tests/test_backend.py
   ```

## Disclaimer

**Facts-only. No investment advice.** This assistant provides only objective data from official sources. For investment recommendations, please consult a SEBI-registered advisor.
