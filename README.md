# AI-Powered Multi-Source Opinion Intelligence Platform

An enterprise-grade, autonomous opinion intelligence platform that transforms natural-language analysis requests and dataset uploads into structured statistical intelligence briefs, interactive web dashboards, and vector PDF reports.

> 📖 **Comprehensive Documentation**: For detailed architecture diagrams, cloud integrations, component-by-component breakdowns, database ER schemas, and deployment guides, refer to [**`SYSTEM_DOCUMENTATION.md`**](SYSTEM_DOCUMENTATION.md).

---

## 1. Quick Start Guide

```
1. Clone Repo     ──► git clone <url> && cd Program
2. Setup Env      ──► Copy .env.example to backend/.env and supply PostgreSQL credentials
3. Python Setup   ──► python -m venv .venv && .venv\Scripts\pip install -r backend/requirements.txt
4. Node Setup     ──► cd frontend && npm install && cd ..
5. Start Backend  ──► .venv\Scripts\python.exe -m uvicorn main:app --app-dir backend --port 8000 --reload
6. Start Frontend ──► cd frontend && npm run dev
7. Open Browser   ──► Access http://localhost:5173
```

---

## 2. Core Architecture & Workflow

```
[User Query / CSV Dataset]
           │
           ▼
[Gemini AI #1: Input Analyzer] ──► Category (PRODUCT, POLICY, TOPIC, URL, DATASET), Target Entity, Queries
           │
           ▼
[Multi-Source Connectors]      ──► Ingest News RSS, Reddit (PRAW), YouTube API, or File Data
           │
           ▼
[Text Sanitization Engine]     ──► Strip URLs/HTML, Deduplicate records
           │
           ▼
[Quantitative Analytics]       ──► VADER Sentiment (-1 to +1), Emotion Radar, TF-IDF + NMF Topics, Forecast
           │
           ▼
[Gemini AI #2: Report Writer]  ──► Strict Fact-Grounded Synthesis (No Hallucinations, Policy Neutrality)
           │
           ▼
[Storage & Output Channels]    ──► PostgreSQL Database, React 19 Dashboard, ReportLab Vector PDF
```

---

## 3. Technology Stack

- **Backend**: Python 3.11+, FastAPI, Uvicorn, Pydantic v2, Pydantic-Settings
- **Database**: PostgreSQL 15+, SQLAlchemy 2.0 AsyncIO, Asyncpg driver
- **AI / LLM**: Google GenAI SDK (`google-genai`), Gemini 2.5 Flash
- **NLP / ML**: scikit-learn, VADER Sentiment, NLTK, Pandas, NumPy, openpyxl
- **Document Generation**: ReportLab
- **Frontend**: React 19, Vite, Tailwind CSS, Recharts, Lucide React, Axios

---

## 4. API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Application health and status check |
| `GET` | `/api/v1/sources/health` | Active connector availability status |
| `POST` | `/api/v1/analyses` | Submit natural-language prompt for analysis |
| `POST` | `/api/v1/analyses/upload` | Upload CSV/Excel dataset for analysis |
| `GET` | `/api/v1/analyses/{id}/status` | Real-time polling endpoint for pipeline execution |
| `GET` | `/api/v1/analyses/{id}/report` | Fetch consolidated intelligence report |
| `GET` | `/api/v1/analyses/{id}/export/pdf` | Stream publication-grade vector PDF report |
| `GET` | `/api/v1/analyses` | Retrieve list of historical analysis briefs |

Interactive Swagger documentation is available at **[http://localhost:8000/docs](http://localhost:8000/docs)**.

---

## 5. Running Automated Tests

Run the complete 15-test automated backend test suite:
```bash
.venv\Scripts\python.exe -m pytest backend/tests/ -v
```

---

## 6. Environment Variables Reference

Copy `.env.example` to `backend/.env` and `.env`:

| Variable | Purpose | Required | Default / Example |
| :--- | :--- | :---: | :--- |
| `DATABASE_URL` | Async PostgreSQL URL | **Yes** | `"postgresql+asyncpg://postgres:postgres@localhost:5432/opinion_intel_db"` |
| `DATABASE_SYNC_URL` | Sync PostgreSQL URL | No | `"postgresql://postgres:postgres@localhost:5432/opinion_intel_db"` |
| `GEMINI_API_KEY` | Google Gemini API Key | Optional | `""` (Uses built-in statistical compiler if blank) |
| `REDDIT_CLIENT_ID` | Reddit App Client ID | Optional | `""` |
| `REDDIT_CLIENT_SECRET` | Reddit Client Secret | Optional | `""` |
| `YOUTUBE_API_KEY` | YouTube Data API Key | Optional | `""` |
| `STORAGE_DIR` | PDF Storage Directory | No | `"./storage/reports"` |
| `MAX_UPLOAD_SIZE_MB` | Upload size limit (MB) | No | `15` |

---

## 7. Complete Reference Manual

For in-depth explanations of every component, data flow examples, troubleshooting guides, security protocols, and production deployment instructions, please see **[`SYSTEM_DOCUMENTATION.md`](SYSTEM_DOCUMENTATION.md)**.
