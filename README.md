# FinSight AI - Investor Intelligence Platform

> End-to-end Financial Document Intelligence Platform using Azure OpenAI, Azure AI Search, Azure PostgreSQL, FastAPI, React, and AKS.

FinSight AI is a comprehensive, AI-powered investor intelligence platform. It processes financial reports, extracts key financial insights and KPIs, generates analytics dashboards, and supports Retrieval-Augmented Generation (RAG) based financial research.

---

## Key Capabilities

* **Financial Report Processing:** Automated ingestion and conversion of PDF annual reports to structured markdown.
* **Semantic Search & Retrieval:** Employs semantic chunking and vector embeddings using Azure AI Search for highly accurate retrieval.
* **KPI Extraction:** Uses Azure OpenAI to automatically extract critical financial metrics (Revenue, Net Income, Cash Flow, Debt, etc.).
* **Dashboard Analytics:** Interactive dashboard providing high-level overviews and document statuses.
* **Company Comparison:** Tools to compare financial metrics and trends across different companies.
* **RAG-Based Financial Research:** Chatbot interface allowing investors to ask complex questions against ingested financial reports (e.g., "Why did revenue increase?", "What are the major risks?").
* **Cloud-Native Architecture:** Designed for deployment on Azure Kubernetes Service (AKS) with containerized frontend and backend.

---

##  Architecture & Workflow

1. **Ingestion:** Financial PDF reports are uploaded and parsed into markdown (using `PyMuPDF4LLM`).
2. **Chunking & Embedding:** Markdown is semantically chunked (via `LangChain`) and embedded using Azure OpenAI.
3. **Vector Storage:** Chunks and embeddings are stored in Azure AI Search for vector and metadata filtering.
4. **KPI Extraction:** Information is extracted via LLMs and structured data is stored in Azure PostgreSQL.
5. **API & UI:** A FastAPI backend serves the React frontend (Dashboard, Analytics, Chat) to end-users.

---

##  Technology Stack

* **Backend:** FastAPI, Python 3.12
* **AI & LLM:** Azure OpenAI, OpenAI, Gemini (Configurable)
* **Vector Search:** Azure AI Search
* **Database:** Azure PostgreSQL (or local SQLite fallback)
* **Package Manager:** UV
* **Deployment:** Docker, Azure Container Registry (ACR), Azure Kubernetes Service (AKS)

---

##  Getting Started

### Prerequisites

* **Python 3.12+**
* **[UV Package Manager](https://github.com/astral-sh/uv)**

### 1. Install UV

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Verify installation: `uv --version`

### 2. Setup Virtual Environment

Create and activate the environment:
```bash
uv venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
uv pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory based on the following template. You only need to configure the services you plan to use (the system falls back to local processing if no API keys are provided).

```env
# Database
DATABASE_URL=sqlite:///data/investor_intelligence.db # Or use PostgreSQL connection string

# Azure OpenAI
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint

# Azure AI Search
AZURE_SEARCH_API_KEY=your_azure_search_api_key
AZURE_SEARCH_ENDPOINT=your_azure_search_endpoint

# Alternative LLM Providers (Optional)
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key
```

### 5. Run the Application

The startup script will automatically initialize the database, create tables, and seed sample data if empty.

```bash
python app.py
```

Access the dashboard at: `http://localhost:8000/`
Access API documentation at: `http://localhost:8000/docs`

---

## 📡 Core API Routes

* **`GET /`** - Renders the main dashboard UI.
* **`/api/ingestion/...`** - Document upload, conversion, and chunking.
* **`/api/chat/...`** - RAG-based AI assistant interactions.
* **`/api/dashboard/...`** - Endpoints serving KPI and analytics data.
* **`/health`** - System health check.

---

##  Notes & Best Practices

* Ensure all Azure resources are properly configured and firewalls allow access from your IP/application before running in production.
* Store secrets in environment variables and never commit `.env` files to source control.
* For production deployments on AKS, utilize Azure Key Vault or Kubernetes Secrets for secure credential management.
