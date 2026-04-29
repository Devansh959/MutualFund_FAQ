# Deployment Plan: Mutual Fund FAQ Assistant

This document outlines the strategy for deploying the Mutual Fund FAQ Assistant across GitHub Actions, Render, and Vercel.

---

## 1. Scheduler: GitHub Actions
The ingestion pipeline will run periodically to keep the facts and vector database updated.

### Configuration
*   **Workflow File**: `.github/workflows/ingest.yml`
*   **Schedule**: Daily at **9:15 AM IST** (03:45 UTC).
*   **Actions**:
    1.  Check out code.
    2.  Set up Python and install dependencies.
    3.  Run `python src/ingestion/run_ingest.py` (which scrapes, processes, embeds, and cleans up).
    4.  **Crucial**: Commit and push the updated `data/vector_db` and `data/processed` files back to the repository so the Backend can pull the latest data.

### Secrets Required
Add these in GitHub Repo Settings -> Secrets and Variables -> Actions:
*   `GOOGLE_API_KEY`: Your Gemini/Google AI API Key.

---

## 2. Backend: Render
The FastAPI backend will handle RAG queries and chat logic.

### Configuration
*   **Service Type**: Web Service
*   **Runtime**: Python
*   **Build Command**: `pip install -r requirements.txt`
*   **Start Command**: `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`
*   **Environment Variables**:
    *   `GOOGLE_API_KEY`: (Secret)
    *   `CHROMA_PATH`: `./data/vector_db`
    *   `COLLECTION_NAME`: `mf_faq_collection`
    *   `EMBEDDING_MODEL_NAME`: `BAAI/bge-base-en-v1.5`
    *   `PYTHON_VERSION`: `3.10.0` (or higher)

### Data Persistence
Since Render's free tier has an ephemeral disk, the backend will pull the latest `data/vector_db` from the GitHub repository on every deploy/restart. For production-grade persistence beyond GitHub commits, a **Render Disk** or **S3 Bucket** is recommended.

---

## 3. Frontend: Vercel
The Streamlit frontend will provide the user interface.

### Deployment Method (Streamlit on Vercel)
Streamlit is a stateful Python server, whereas Vercel is optimized for serverless/static content. To run Streamlit on Vercel:

*   **Runtime**: Use the `vercel-python` community runtime.
*   **Configuration**: Create a `vercel.json` in the root:
    ```json
    {
      "builds": [
        {
          "src": "app.py",
          "use": "@vercel/python"
        }
      ],
      "routes": [
        {
          "src": "/(.*)",
          "dest": "app.py"
        }
      ]
    }
    ```
*   **Environment Variables**:
    *   `BACKEND_URL`: The URL of your Render service (e.g., `https://mf-faq-backend.onrender.com`).

### Alternative Recommendation
If Vercel's serverless timeouts interfere with Streamlit's long-polling:
*   **Streamlit Community Cloud**: Direct integration with GitHub, free and optimized for Streamlit.
*   **Render**: Deploy the frontend as a second "Web Service" on Render.

---

## 4. CI/CD Pipeline Summary

1.  **Code Push**: Developer pushes to `main`.
2.  **Vercel & Render Deploy**: Both platforms automatically trigger a redeploy of the latest code.
3.  **Daily Ingestion**: GitHub Actions runs at 9:15 AM IST, updates the JSON/Vector files, and commits them to `main`.
4.  **Auto-Update**: Render/Vercel (if configured with auto-deploy) will see the new commit from GitHub Actions and refresh the service with the latest mutual fund data.

---

## 5. Pre-Deployment Checklist
- [ ] Verify `.env` variables are correctly mapped to platform secrets.
- [ ] Ensure `requirements.txt` includes `uvicorn`, `fastapi`, and all ingestion dependencies.
- [ ] Test the `run_ingest.py` script one last time locally to ensure no file path issues.
- [ ] Update `app.py` to use an environment variable for the `BASE_URL` of the backend instead of `localhost:8000`.
