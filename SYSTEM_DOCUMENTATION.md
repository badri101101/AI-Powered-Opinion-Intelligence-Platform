# SYSTEM DOCUMENTATION
## AI-Powered Multi-Source Opinion Intelligence Platform

---

## 1. Project Overview

### 1.1 Project Name & Purpose
The **AI-Powered Multi-Source Opinion Intelligence Platform** is an enterprise-grade automated opinion research system. It ingests natural-language analysis requests or uploaded datasets, orchestrates multi-platform data harvesting across public channels, applies statistical natural language processing (NLP) and machine learning algorithms, and produces evidence-grounded intelligence reports alongside publication-grade vector PDF documents.

### 1.2 Problem It Solves
Traditional opinion research and sentiment monitoring suffer from three key bottlenecks:
1. **Manual Data Sifting**: Extracting actionable themes across disparate platforms (News, Reddit, YouTube, customer reviews) is labor-intensive.
2. **LLM Hallucinations**: Standard conversational LLMs frequently invent statistics, fabricate quotes, or display political/ideological bias when asked about public discourse.
3. **Lack of Structured Quantitative Grounding**: Qualitative summaries fail to give decision-makers exact sentiment polarity scores, affective emotion distributions, thematic volume shares, and statistical momentum trajectories.

This platform bridges this gap by decoupling **quantitative data computation** (handled deterministically by VADER, scikit-learn, and NMF) from **qualitative report synthesis** (handled by Gemini AI #2 strictly referencing computed facts).

### 1.3 Who Can Use It
- **Product Managers & Market Researchers**: To assess customer reception, feature feedback, and brand comparisons (e.g., "Analyze Samsung Galaxy S26 reviews").
- **Policy Analysts & Civic Researchers**: To measure public discourse and concerns regarding legislative or regulatory initiatives with strict neutrality (e.g., "Analyze public discussion about the new EV policy in India").
- **Data Analysts & Business Intelligence Teams**: To upload tabular survey datasets (`.csv`, `.xlsx`) and instantly produce executive KPI briefs.

### 1.4 Main Workflow
```
[User Input: Prompt or File Upload]
                │
                ▼
[Gemini AI #1: Input Analyzer]  ──► Category, Target Entity, Scope, Connector Queries
                │
                ▼
[Multi-Source Connectors]       ──► Harvest News, Reddit, YouTube, or Files
                │
                ▼
[Text Preprocessor]             ──► HTML sanitization, URL removal, Deduplication
                │
                ▼
[Analytics Engine]              ──► Sentiment (-1 to +1), Emotions, NMF Topics, Forecasting
                │
                ▼
[Gemini AI #2: Report Writer]   ──► Fact-Grounded Narrative Synthesis (No Hallucinations)
                │
                ▼
[Storage & Output]              ──► PostgreSQL Database, React Dashboard, ReportLab PDF
```

### 1.5 Main Features
- **Deterministic Category & Scope Detection**: Classifies requests into `PRODUCT`, `POLICY`, `TOPIC`, `URL`, or `DATASET`.
- **Multi-Source Data Connectors**: Supports Google News RSS, Reddit API (PRAW), YouTube Data API v3, and CSV/Excel uploads.
- **Statistical NLP Engine**:
  - VADER compound sentiment polarity scoring.
  - 5-dimensional affective emotion breakdown (Joy, Trust, Surprise, Sadness, Anger).
  - Unsupervised thematic topic clustering via TF-IDF + NMF.
  - Named entity mention frequency and aspect-level sentiment mapping.
  - Linear regression trend velocity and forecast projections with confidence bounds.
- **Fact-Grounded Executive Synthesis**: Gemini 2.5 Flash compiles executive summaries and strategic takeaways citing strictly calculated numbers.
- **Policy & Political Neutrality Guardrails**: Strictly prevents subjective speculation on election outcomes or partisanship.
- **Vector PDF Generator**: ReportLab-powered document generator with KPI scorecards, topic matrices, and source attribution audit tables.
- **Interactive Web Dashboard**: React 19 + Tailwind CSS + Recharts UI with real-time stage progress polling and historical runs drawer.

### 1.6 What the Application Does NOT Do
- **No Conversational Chat History**: The application is an analytics product, not a chatbot. Every request initiates a discrete, isolated analysis session with a unique UUID.
- **No Direct Remote Database SQL Execution**: Does not expose raw database execution to external prompts.
- **No DOCX or MongoDB**: Uses vector PDF generation (ReportLab) and relational PostgreSQL storage.

---

## 2. System Architecture

```mermaid
graph TD
    User([User / Web Browser]) <-->|HTTP / JSON REST API| Frontend[React 19 + Vite + Tailwind Dashboard]
    
    subgraph Backend [FastAPI Backend Service]
        Router[API Layer - /api/v1/analyses]
        Orchestrator[Asynchronous Workflow Orchestrator]
        
        subgraph AIServices [AI Intelligence Layer]
            AI1[Gemini AI #1: Input & Workflow Analyzer]
            AI2[Gemini AI #2: Fact-Grounded Report Writer]
        end
        
        subgraph SourceLayer [Data Ingestion Layer]
            NewsConn[News/RSS Connector - feedparser]
            RedditConn[Reddit Connector - PRAW]
            YTConn[YouTube Data API Connector]
            FileConn[CSV/Excel Parser - pandas]
        end
        
        subgraph AnalyticsLayer [Statistical Analytics & NLP Engine]
            Preproc[Text Preprocessor & Deduplicator]
            SentEng[VADER Sentiment Engine]
            EmoEng[Affective Emotion Classifier]
            TopicEng[TF-IDF + NMF Topic Clusterer]
            TrendEng[Time-Series & Linear Regression Forecast]
        end
        
        subgraph ExportLayer [Export & Publishing]
            PDFBuilder[ReportLab Vector PDF Builder]
        end
    end
    
    subgraph DataStorage [Data Persistence Layer]
        PG[(PostgreSQL Database)]
        PDFStore[(Local Storage / storage/reports/)]
    end
    
    subgraph CloudAPIs [External Cloud & Platform APIs]
        GeminiCloud[Google Gemini 2.5 Flash API]
        GoogleNews[Google News RSS Feeds]
        RedditAPI[Reddit API]
        YouTubeAPI[Google YouTube Data API v3]
    end

    Frontend -->|POST /analyses| Router
    Router -->|Launch Background Task| Orchestrator
    Orchestrator -->|1. Classify Intent| AI1
    AI1 <--> GeminiCloud
    Orchestrator -->|2. Harvest Data| SourceLayer
    NewsConn <--> GoogleNews
    RedditConn <--> RedditAPI
    YTConn <--> YouTubeAPI
    Orchestrator -->|3. Clean & Analyze| AnalyticsLayer
    AnalyticsLayer --> Preproc
    Preproc --> SentEng & EmoEng & TopicEng & TrendEng
    Orchestrator -->|4. Synthesize Report| AI2
    AI2 <--> GeminiCloud
    Orchestrator -->|5. Generate PDF| PDFBuilder
    PDFBuilder --> PDFStore
    Orchestrator -->|6. Persist Audit State| PG
    Router -->|GET /status & /report| Frontend
    PDFBuilder -->|Download Stream| Frontend
```

---

## 3. Component-by-Component Explanation

### 3.1 Frontend Layer
- **Implementation**: `frontend/src/`
- **Technology**: React 19, Vite, Tailwind CSS, Recharts, Lucide React, Axios.
- **Purpose**: Provides a modern, responsive single-page application (SPA) with three operational views:
  1. `INPUT`: Search bar with category selector, prompt suggestions, and drag-and-drop CSV/Excel upload zone.
  2. `PROGRESS`: Real-time execution stepper showing live backend pipeline stages.
  3. `REPORT`: Complete intelligence brief featuring executive summary, sentiment meters, emotion radars, topic cards, time-series charts, and verified source table.

### 3.2 Backend Layer & API Router
- **Implementation**: `backend/main.py`, `backend/app/api/v1/`
- **Technology**: FastAPI, Pydantic v2, Python 3.11+.
- **Purpose**: Serves REST API endpoints, coordinates asynchronous background execution using `FastAPI.BackgroundTasks`, handles file uploads with validation, and manages CORS policies.

### 3.3 Database Layer (PostgreSQL & Async SQLAlchemy)
- **Implementation**: `backend/app/core/database.py`, `backend/app/models/`
- **Technology**: PostgreSQL 15+, SQLAlchemy 2.0 AsyncIO, Asyncpg driver.
- **Purpose**: Persists analysis requests, collected records, quantitative metrics, and finalized reports with complete data integrity and cascade deletions.

### 3.4 Gemini AI #1 (Input & Workflow Analyzer)
- **Implementation**: `backend/app/services/ai/input_analyzer.py`
- **Technology**: `google-genai` SDK (`gemini-2.5-flash`), Pydantic structured output.
- **Input**: Raw natural language prompt or URL.
- **Output**: `InputAnalysisSpec` containing category, target entity, location scope, timeframe, recommended sources, and optimized connector search queries.
- **Fallback**: Built-in deterministic regex/keyword classifier for offline execution.

### 3.5 Data Connectors
- **Implementation**: `backend/app/services/connectors/`
- **Connectors**:
  - `news_conn.py`: Google News RSS feed parser with automatic article metadata and publish date extraction.
  - `reddit_conn.py`: PRAW integration for querying submissions and top-level comment trees.
  - `youtube_conn.py`: Google API Client for harvesting video metadata and top viewer comments.
  - `file_conn.py`: Pandas parser with dynamic text, date, and author column detection for CSV and Excel files.
- **Output**: Standardized `List[NormalizedRecord]`.

### 3.6 Data Preprocessor
- **Implementation**: `backend/app/services/analytics/preprocessor.py`
- **Purpose**: Strips raw URLs and HTML tags, unescapes entities, normalizes whitespace, filters short spam (<5 characters), and deduplicates records by hashing text prefixes.

### 3.7 Quantitative Analytics Engine
- **Implementation**: `backend/app/services/analytics/`
- **Sub-modules**:
  - `sentiment.py`: VADER scoring mapping compound polarity (-1.00 to +1.00) into Positive, Neutral, Negative percentages and descriptive labels.
  - `emotions.py`: Lexical density scoring for Joy, Trust, Surprise, Sadness, and Anger.
  - `topics.py`: TF-IDF vectorizer + Non-Negative Matrix Factorization (NMF) clustering producing cluster names, top keywords, volume shares, and cluster sentiment polarities.
  - `entities.py`: Frequency and sentiment extractor for capitalized brand names, products, and key terms.
  - `forecasting.py`: Daily sentiment time-series aggregator and linear regression model calculating slope velocity and future trajectory with 95% confidence intervals.
- **Output**: Consolidated `AnalysisMetricsDTO`.

### 3.8 Gemini AI #2 (Fact-Grounded Report Generator)
- **Implementation**: `backend/app/services/ai/report_writer.py`
- **Technology**: `google-genai` SDK (`gemini-2.5-flash`).
- **Input**: Structured JSON facts containing computed metrics, topic summaries, and source attribution metadata.
- **Output**: `ReportSynthesisSpec` containing executive title, narrative summary, structured key findings, topic summaries, trend narrative, and policy neutrality disclaimers.
- **Fallback**: Deterministic statistical report compiler ensuring report generation succeeds even during API rate limits or network outages.

### 3.9 PDF Export Builder
- **Implementation**: `backend/app/services/export/pdf_builder.py`, `backend/app/services/export/pdf_styles.py`
- **Technology**: ReportLab.
- **Purpose**: Generates publication-quality vector PDF reports with custom canvas page numbering, colored KPI scorecards, thematic cluster tables, and verified source audit logs.

### 3.10 Configuration & Environment System
- **Implementation**: `backend/app/config.py`
- **Technology**: `pydantic-settings` (`BaseSettings`, `SettingsConfigDict`).
- **Purpose**: Loads environment variables from `.env` and `backend/.env` with safe defaults, typed validation, and runtime inspection.

---

## 4. Complete Data Flow

### Example: "Analyze Samsung Galaxy S26 reviews"

1. **User Request**: User enters *"Analyze Samsung Galaxy S26 reviews"* in the web UI and clicks **Analyze**.
2. **API Dispatch**: Frontend sends `POST /api/v1/analyses` with payload `{"prompt": "Analyze Samsung Galaxy S26 reviews"}`.
3. **Session Creation**: Backend generates a new `UUID`, creates a row in `analysis_requests` with status `PENDING`, and spawns an asynchronous background worker via `orchestrator.run_pipeline(analysis_id)`. Returns HTTP `202 Accepted` with the session ID.
4. **Intent Analysis (Gemini AI #1)**:
   - Status updates to `CLASSIFYING` (15%).
   - Prompt is sent to Gemini 2.5 Flash with structured schema instructions.
   - Analyzer classifies: `category = "PRODUCT"`, `target_entity = "Samsung Galaxy S26"`, `recommended_sources = ["NEWS", "REDDIT", "YOUTUBE"]`, `queries = {"news_query": "Samsung Galaxy S26", "reddit_query": "Samsung Galaxy S26", "youtube_query": "Samsung Galaxy S26 review"}`.
5. **Multi-Source Collection**:
   - Status updates to `COLLECTING` (35%).
   - News connector harvests Google News RSS entries for *"Samsung Galaxy S26"*.
   - Reddit and YouTube connectors query configured platforms.
   - Raw records are normalized into `NormalizedRecord` format and saved to `collected_records`.
6. **Preprocessing & Deduplication**:
   - Text preprocessor unescapes HTML, strips tracking URLs, and eliminates duplicates.
7. **Quantitative Analytics**:
   - Status updates to `ANALYZING` (65%).
   - VADER computes polarity for every record (e.g. 68% Positive, 22% Neutral, 10% Negative, Compound: +0.48).
   - Emotion analyzer computes affective scores (e.g. Joy: 42%, Trust: 35%, Anger: 8%).
   - TF-IDF + NMF identifies thematic clusters (e.g. Cluster 1: *"Display & Screen"*, Cluster 2: *"Camera & Night Photos"*, Cluster 3: *"Battery & Charging"*).
   - Forecasting engine aggregates daily sentiment points and computes linear regression slope.
   - Metrics are committed to `analysis_metrics`.
8. **Report Synthesis (Gemini AI #2)**:
   - Status updates to `GENERATING` (85%).
   - Quantified statistics are packaged into structured JSON and sent to Gemini AI #2.
   - Gemini compiles executive summary, strategic takeaway cards, and topic summaries referencing strictly the computed figures.
9. **PDF Document Compilation**:
   - ReportLab renders a multi-page vector PDF saved to `storage/reports/report_{id}.pdf`.
   - Report row is committed to `generated_reports`.
10. **Completion & Real-Time Dashboard Rendering**:
    - Status updates to `COMPLETED` (100%).
    - Frontend polling detects `COMPLETED` and requests `GET /api/v1/analyses/{id}/report`.
    - Dashboard renders the complete opinion brief.
    - User can click **Export PDF Report** to stream the document from `GET /api/v1/analyses/{id}/export/pdf`.

---

## 5. Dataset Upload Workflow

### Supported Formats & File Specifications
- **Accepted File Formats**: `.csv`, `.xlsx`, `.xls`
- **Maximum File Size**: 15 MB (configurable via `MAX_UPLOAD_SIZE_MB`)
- **Auto-Detected Columns**:
  - *Text column*: Priority search for `review`, `comment`, `text`, `feedback`, `opinion`, `content`, `body`, `message`, `description`. Falls back to the column with the highest average string length.
  - *Timestamp column*: Automatically checks for `date`, `time`, `timestamp`, `created_at`, `published_at`.
  - *Author column*: Priority search for `author`, `user`, `username`, `reviewer`, `name`.
  - *Rating / Engagement*: Checks for `rating`, `score`, `likes`, `upvotes`, `stars`.

### Step-by-Step Upload Flow
1. User clicks the **Upload Dataset** tab on the homepage.
2. User drags and drops a CSV or Excel file (e.g., `customer_survey.csv`) and optionally provides context.
3. Frontend sends `POST /api/v1/analyses/upload` with `multipart/form-data`.
4. Backend validates file extension and size, parses rows into `NormalizedRecord` objects, and assigns category `DATASET`.
5. Orchestrator executes standard preprocessing, sentiment scoring, emotion density detection, NMF clustering, trend forecasting, report synthesis, and PDF generation.
6. Full dashboard renders with source platform labeled as `FILE_UPLOAD`.

---

## 6. User Actions & Interface Guide

| View | User Action | System Response |
| :--- | :--- | :--- |
| **Landing Page** | Enter prompt (e.g., *"Analyze Samsung Galaxy S26 reviews"*) and click **Analyze** | Initiates pipeline, switches to Stepper View |
| **Landing Page** | Click an example prompt pill | Auto-fills search input |
| **Landing Page** | Drag and drop CSV / Excel file | Validates file and begins dataset analysis |
| **Landing Page** | Click **Category** filter button | Allows manual override of classification intent |
| **Progress View** | View live execution stepper | Polls `/analyses/{id}/status` every 1.5s, updates progress bar |
| **Report Dashboard** | Inspect Executive Summary & Takeaways | Displays structured findings with Positive/Negative/Neutral tags |
| **Report Dashboard** | View Sentiment & Emotion Meters | Interactive bars and metrics normalized to 100% |
| **Report Dashboard** | Explore Thematic Topic Clusters | Displays cluster cards with keywords, share %, and polarities |
| **Report Dashboard** | Inspect Temporal Momentum & Forecast | Recharts line chart with historical momentum and projected intervals |
| **Report Dashboard** | Review Source Ingestion Audit Table | Shows connector names, queries executed, record counts, and timestamps |
| **Report Dashboard** | Click **Export PDF Report** | Triggers instantaneous download of ReportLab vector PDF |
| **Header** | Click **History** button | Opens slide-over drawer displaying past analyses; click to open any report |
| **Header** | Click **New Analysis** or Logo | Resets view to clean search bar (each analysis is independent) |

---

## 7. Cloud Operations & External APIs

### 7.1 Google Gemini AI Integration
- **Model Used**: `gemini-2.5-flash` (via official `google-genai` SDK).
- **Operations Using Gemini**:
  1. *Input & Workflow Analyzer (AI #1)*: Extracts category, target entity, location scope, and connector search terms.
  2. *Report Generator (AI #2)*: Synthesizes high-level executive narrative and takeaway insights.
- **What is Sent to Gemini**:
  - AI #1 receives only the user's natural-language query string.
  - AI #2 receives aggregated statistical numbers, topic labels, keyword arrays, and source names.
- **What is NOT Sent to Gemini**:
  - Bulk raw comment datasets (saving token costs and preventing hallucinations).
  - Database connection strings, credentials, or internal configuration details.
- **Validation & Guardrails**:
  - Gemini responses are strictly constrained to Pydantic JSON schemas via `response_schema`.
  - If Gemini output fails validation or API quota is exceeded, built-in deterministic compilers immediately generate the report without crashing.

### 7.2 External Platform APIs
- **Google News / RSS**:
  - *Purpose*: Gathers public news coverage and editorial reviews.
  - *Auth*: Open RSS endpoint (no API key required).
  - *Fallback*: Always active.
- **Reddit API (PRAW)**:
  - *Purpose*: Gathers Reddit community discussions and user comments.
  - *Auth*: OAuth client credentials (`REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT`).
  - *Fallback*: If credentials are missing, system logs notification and continues with available connectors.
- **YouTube Data API v3**:
  - *Purpose*: Gathers video metadata and viewer comment threads.
  - *Auth*: API Key (`YOUTUBE_API_KEY`).
  - *Fallback*: If key is missing, system gracefully skips YouTube ingestion.

---

## 8. Database Architecture

### 8.1 Database Technology
- **Engine**: PostgreSQL 15+
- **Driver**: `asyncpg` via SQLAlchemy 2.0 AsyncIO
- **Connection Management**: `NullPool` to prevent cross-event-loop connection sharing in async background workers.

### 8.2 Entity-Relationship (ER) Diagram

```mermaid
erDiagram
    ANALYSIS_REQUESTS ||--o{ SOURCE_METADATA : "has sources"
    ANALYSIS_REQUESTS ||--o{ COLLECTED_RECORDS : "contains"
    ANALYSIS_REQUESTS ||--o| ANALYSIS_METRICS : "computes"
    ANALYSIS_REQUESTS ||--o| GENERATED_REPORTS : "produces"

    ANALYSIS_REQUESTS {
        uuid id PK
        text original_prompt
        varchar category
        varchar target_entity
        varchar location_scope
        integer time_period_days
        json intent_parameters
        varchar status
        varchar current_step
        integer progress_percent
        integer records_found
        text error_message
        timestamp created_at
        timestamp completed_at
    }

    SOURCE_METADATA {
        uuid id PK
        uuid analysis_id FK
        varchar platform
        text source_url
        text query_used
        integer records_collected
        varchar status
        text error_message
        timestamp fetched_at
    }

    COLLECTED_RECORDS {
        uuid id PK
        uuid analysis_id FK
        varchar platform
        text external_id
        text raw_text
        text cleaned_text
        text author
        timestamp published_at
        integer engagement_score
        text source_url
        json record_metadata
        timestamp created_at
    }

    ANALYSIS_METRICS {
        uuid id PK
        uuid analysis_id FK
        integer total_records_analyzed
        json sentiment_distribution
        json emotion_scores
        json topic_clusters
        json entity_mentions
        json time_series_trends
        json forecast_data
        timestamp computed_at
    }

    GENERATED_REPORTS {
        uuid id PK
        uuid analysis_id FK
        varchar report_title
        text executive_summary
        json key_findings
        json topic_summaries
        text trend_narrative
        text forecast_interpretation
        text caveats_and_disclaimers
        varchar pdf_file_path
        timestamp generated_at
    }
```

---

## 9. Frontend Architecture

### 9.1 Structure & Key Modules
- `frontend/src/api/`: Axios HTTP client and typed analysis API wrapper (`client.js`, `analysesApi.js`).
- `frontend/src/components/common/`: Reusable UI primitives (`Button.jsx`, `Card.jsx`, `Badge.jsx`, `Header.jsx`, `Footer.jsx`).
- `frontend/src/components/input/`: Search input bar (`AnalysisInputBar.jsx`), prompt suggestions (`ExamplePrompts.jsx`), and drag-and-drop file upload (`FileUploadZone.jsx`).
- `frontend/src/components/progress/`: Real-time execution stepper (`ExecutionStepper.jsx`).
- `frontend/src/components/dashboard/`:
  - `ReportHeader.jsx`: Title, metadata pills, PDF export trigger.
  - `ExecutiveSummary.jsx`: Synthesis narrative and key takeaway cards.
  - `SentimentOverview.jsx`: Compound polarity meter, normalized distribution bar, emotion breakdown.
  - `TopicGrid.jsx`: Thematic cluster cards with keywords, share %, and polarities.
  - `TrendTimeSeries.jsx`: Recharts time-series chart with linear regression forecast indicators.
  - `SourceAttribution.jsx`: Verified connector audit table with status and timestamps.
  - `CaveatsDisclaimer.jsx`: Transparency and methodology notice.
- `frontend/src/components/history/`: `RecentAnalysesDrawer.jsx` for browsing past runs.

### 9.2 UI Design Principles
- **Restrained Professional Aesthetic**: High-legibility slate typography (`text-slate-900`, `text-slate-600`), neutral backgrounds (`bg-slate-50`), subtle borders (`border-slate-200`), and minimal shadows.
- **Accurate Visual Data Representation**: Color-coded sentiment badges (Emerald for Positive, Slate for Neutral, Rose for Negative), responsive chart containers, and zero decorative fluff.

---

## 10. Backend Architecture & API Specifications

### 10.1 Endpoints Table

| Method | Endpoint | Purpose | Request Body | Response Body |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/health` | System health check | None | `{"status": "healthy", "version": "1.0.0"}` |
| `GET` | `/api/v1/sources/health` | Check status of active data connectors | None | `SourceHealthDTO` |
| `POST` | `/api/v1/analyses` | Initiate analysis from natural language prompt | `{"prompt": "...", "category_override": null}` | `AnalysisStatusResponse` (HTTP 202) |
| `POST` | `/api/v1/analyses/upload` | Initiate analysis from uploaded dataset | `multipart/form-data` (`file`, optional `prompt`) | `AnalysisStatusResponse` (HTTP 202) |
| `GET` | `/api/v1/analyses/{id}/status` | Poll real-time pipeline execution progress | None | `AnalysisStatusResponse` |
| `GET` | `/api/v1/analyses/{id}/report` | Retrieve complete consolidated intelligence report | None | `FullReportResponse` |
| `GET` | `/api/v1/analyses/{id}/export/pdf` | Download publication-grade vector PDF report | None | `application/pdf` binary stream |
| `GET` | `/api/v1/analyses` | List recent analysis sessions | Query params: `limit`, `offset` | `AnalysisListResponse` |

---

## 11. Project Folder Structure

```
Program/
├── .env.example                       # Environment configuration template
├── .gitignore                          # Comprehensive Git ignore definitions
├── pytest.ini                          # Pytest configuration and asyncio mode settings
├── README.md                           # Quick-start guide and project overview
├── SYSTEM_DOCUMENTATION.md             # Complete system architecture and reference manual
│
├── backend/                            # FastAPI Backend Application
│   ├── requirements.txt                # Python backend dependencies
│   ├── main.py                         # Application entrypoint & lifespan management
│   ├── app/
│   │   ├── config.py                   # Pydantic-Settings environment loader
│   │   ├── api/                        # API route controllers
│   │   │   ├── router.py               # Root v1 router
│   │   │   └── v1/
│   │   │       ├── analyses.py         # Analysis creation, status, report & PDF endpoints
│   │   │       └── sources.py          # Data source health status endpoint
│   │   ├── core/
│   │   │   └── database.py             # Async SQLAlchemy engine & session factory
│   │   ├── models/                     # SQLAlchemy ORM database models
│   │   │   ├── analysis.py             # AnalysisRequest model & status enums
│   │   │   ├── source_data.py          # SourceMetadata & CollectedRecord models
│   │   │   ├── metrics.py              # AnalysisMetrics model
│   │   │   └── report.py               # GeneratedReport model
│   │   ├── schemas/                    # Pydantic DTO models & serialization contracts
│   │   │   ├── ai_specs.py             # Gemini AI #1 & AI #2 schema contracts
│   │   │   ├── analysis.py             # Request & status schemas
│   │   │   ├── metrics.py              # Statistical metrics DTOs
│   │   │   ├── report.py               # Report response DTOs
│   │   │   └── source.py               # Source metadata & health DTOs
│   │   └── services/                   # Core business logic & pipeline services
│   │       ├── orchestrator.py         # End-to-end workflow orchestrator
│   │       ├── ai/                     # Gemini integration services
│   │       │   ├── gemini_client.py    # Official Google GenAI SDK client
│   │       │   ├── input_analyzer.py   # Gemini AI #1: Intent & query extractor
│   │       │   └── report_writer.py    # Gemini AI #2: Fact-grounded report synthesizer
│   │       ├── connectors/             # Data ingestion connectors
│   │       │   ├── base.py             # Abstract base connector class
│   │       │   ├── news_conn.py        # Google News RSS connector
│   │       │   ├── reddit_conn.py      # Reddit PRAW connector
│   │       │   ├── youtube_conn.py     # YouTube Data API v3 connector
│   │       │   └── file_conn.py        # CSV/Excel dataset parser
│   │       ├── analytics/              # NLP & ML analytics algorithms
│   │       │   ├── preprocessor.py     # Text cleaning & deduplication
│   │       │   ├── sentiment.py        # VADER sentiment scoring
│   │       │   ├── emotions.py         # Affective emotion scoring
│   │       │   ├── topics.py           # TF-IDF + NMF topic clustering
│   │       │   ├── entities.py         # Named entity extraction
│   │       │   ├── forecasting.py      # Linear regression forecasting
│   │       │   └── engine.py           # Master analytics engine aggregator
│   │       └── export/                 # Document generation
│   │           ├── pdf_styles.py       # ReportLab styles & palette definitions
│   │           └── pdf_builder.py      # Vector PDF document builder
│   └── tests/                          # Automated backend test suite
│       ├── conftest.py                 # Async test client & database fixtures
│       ├── test_api_endpoints.py       # API route & orchestration tests
│       ├── test_input_analyzer.py      # Gemini AI #1 intent classification tests
│       ├── test_analytics_engine.py    # Statistical analytics engine tests
│       ├── test_pdf_builder.py         # PDF generation tests
│       └── test_edge_cases.py          # Edge case, error & fallback tests
│
└── frontend/                           # React 19 SPA (Vite + Tailwind CSS)
    ├── package.json                    # Frontend dependencies & build scripts
    ├── vite.config.js                  # Vite bundler configuration
    ├── postcss.config.js               # PostCSS configuration with Tailwind v4
    ├── index.html                      # Single-page HTML template
    └── src/
        ├── main.jsx                    # React application entrypoint
        ├── App.jsx                     # Master view controller & polling state machine
        ├── index.css                   # Global Tailwind CSS imports
        ├── api/                        # Axios API integration
        │   ├── client.js               # Axios instance with base URL configuration
        │   └── analysesApi.js          # REST API caller methods
        └── components/                 # Component library
            ├── common/                 # Common UI components (Header, Footer, Badge, Button, Card)
            ├── input/                  # Search bar, example prompts, file upload
            ├── progress/               # Live pipeline execution stepper
            ├── dashboard/              # Report widgets (Executive, Sentiment, Topics, Trends, Sources)
            └── history/                # Recent runs history drawer
```

---

## 12. Dependencies & Versions

### 12.1 System Requirements
- **Python**: `3.11`, `3.12`, `3.13`, or `3.14`
- **Node.js**: `v18.0.0+` (LTS recommended)
- **PostgreSQL**: `14.0+`

### 12.2 Python Dependencies (`backend/requirements.txt`)
- `fastapi` & `uvicorn`: High-performance asynchronous web framework.
- `pydantic` & `pydantic-settings`: Data validation, serialization, and environment management.
- `SQLAlchemy` & `asyncpg`: Async ORM and PostgreSQL driver.
- `google-genai`: Official Google Gemini SDK for structured AI operations.
- `praw`: Python Reddit API Wrapper.
- `google-api-python-client`: Official client for YouTube Data API v3.
- `feedparser`: Robust XML/RSS parser for Google News.
- `pandas`, `numpy`, `openpyxl`: Dataset parsing and numeric data manipulation.
- `scikit-learn`: TF-IDF vectorization and Non-Negative Matrix Factorization (NMF).
- `vaderSentiment`: Rule-based sentiment analysis tuned for social media and reviews.
- `reportlab`: PDF document creation engine.
- `pytest` & `pytest-asyncio`: Automated async testing framework.

### 12.3 Frontend Dependencies (`frontend/package.json`)
- `react` & `react-dom` (v19): Modern UI component framework.
- `tailwindcss` & `@tailwindcss/postcss` (v4): Utility-first CSS styling.
- `recharts`: Composable SVG charting library for time-series trajectories.
- `lucide-react`: Lightweight, modern icon library.
- `axios`: Promise-based HTTP client for browser requests.

---

## 13. Environment Variables Reference

| Variable | Purpose | Required | Safe Placeholder / Default |
| :--- | :--- | :---: | :--- |
| `APP_NAME` | Application display name | No | `"AI-Powered Multi-Source Opinion Intelligence Platform"` |
| `ENVIRONMENT` | Runtime environment (`development` / `production`) | No | `"development"` |
| `DEBUG` | Enable debug logging | No | `True` |
| `HOST` | Backend server bind address | No | `"0.0.0.0"` |
| `PORT` | Backend server port | No | `8000` |
| `CORS_ORIGINS` | Permitted frontend origins list | No | `["http://localhost:5173","http://127.0.0.1:5173"]` |
| `DATABASE_URL` | Async PostgreSQL connection string | **Yes** | `"postgresql+asyncpg://postgres:postgres@localhost:5432/opinion_intel_db"` |
| `DATABASE_SYNC_URL` | Synchronous PostgreSQL connection string | No | `"postgresql://postgres:postgres@localhost:5432/opinion_intel_db"` |
| `GEMINI_API_KEY` | Google Gemini API Key | Optional (Has fallback) | `""` |
| `GEMINI_ANALYZER_MODEL` | Gemini model for Input Analyzer (AI #1) | No | `"gemini-2.5-flash"` |
| `GEMINI_REPORT_MODEL` | Gemini model for Report Generator (AI #2) | No | `"gemini-2.5-flash"` |
| `REDDIT_CLIENT_ID` | Reddit App Client ID | Optional | `""` |
| `REDDIT_CLIENT_SECRET` | Reddit App Client Secret | Optional | `""` |
| `REDDIT_USER_AGENT` | Reddit user agent header | No | `"opinion-intel-app:v1.0"` |
| `YOUTUBE_API_KEY` | Google YouTube Data API v3 Key | Optional | `""` |
| `STORAGE_DIR` | Directory for generated PDF files | No | `"./storage/reports"` |
| `MAX_UPLOAD_SIZE_MB` | Maximum dataset upload size in MB | No | `15` |

---

## 14. Installation & Setup Guide (From Clean Clone)

### Step 1: Install System Prerequisites
1. Install **Python 3.11+** from [python.org](https://www.python.org/) (ensure *"Add Python to PATH"* is checked).
2. Install **Node.js 18+** from [nodejs.org](https://nodejs.org/).
3. Install and start **PostgreSQL** from [postgresql.org](https://www.postgresql.org/).

### Step 2: Clone Repository
```bash
git clone <repository-url>
cd Program
```

### Step 3: Configure Database
Open your PostgreSQL shell (`psql` or pgAdmin) and create the database:
```sql
CREATE DATABASE opinion_intel_db;
```

### Step 4: Configure Environment Files
Copy `.env.example` to `backend/.env` and `.env`:
```bash
# On Windows PowerShell:
Copy-Item .env.example .env
Copy-Item .env.example backend\.env
```
Open `backend/.env` in a text editor and supply your PostgreSQL credentials and optional API keys:
```env
DATABASE_URL="postgresql+asyncpg://postgres:your_password@localhost:5432/opinion_intel_db"
GEMINI_API_KEY="your_gemini_api_key_here"
```

### Step 5: Set Up Python Backend
```bash
# Create Python virtual environment
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.venv\Scripts\Activate.ps1
# On Windows Command Prompt:
# .venv\Scripts\activate.bat
# On Linux / macOS:
# source .venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt
```

### Step 6: Set Up Frontend
```bash
cd frontend
npm install
cd ..
```

### Step 7: Launch Backend & Frontend
1. **Start Backend** (Terminal 1):
```bash
.venv\Scripts\python.exe -m uvicorn main:app --app-dir backend --host 0.0.0.0 --port 8000 --reload
```
2. **Start Frontend** (Terminal 2):
```bash
cd frontend
npm run dev -- --host
```

### Step 8: Access the Platform
- Open **[http://localhost:5173](http://localhost:5173)** in your browser.
- Verify backend API docs at **[http://localhost:8000/docs](http://localhost:8000/docs)**.

---

## 15. Windows Platform Notes

- **PowerShell Script Execution Policy**: If `.venv\Scripts\Activate.ps1` gives an execution policy error, run:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
- **Direct Python Invocation**: You can run commands directly using `.venv\Scripts\python.exe` without explicitly activating the shell.
- **Port Conflicts**: If port 8000 or 5173 is in use:
  - Backend: Change `--port 8001` and update `frontend/src/api/client.js`.
  - Frontend: Change `npm run dev -- --port 5174`.

---

## 16. Quick-Start Workflow

```
1. Clone Repo     ──► git clone <url> && cd Program
2. Setup Env      ──► Copy .env.example to backend/.env and configure DB password
3. Python Setup   ──► python -m venv .venv && .venv\Scripts\pip install -r backend/requirements.txt
4. Node Setup     ──► cd frontend && npm install && cd ..
5. Launch Backend ──► .venv\Scripts\python.exe -m uvicorn main:app --app-dir backend --port 8000
6. Launch Front   ──► cd frontend && npm run dev
7. Analyze        ──► Open http://localhost:5173 and enter an opinion prompt!
```

---

## 17. Troubleshooting Guide

| Issue | Root Cause | Solution |
| :--- | :--- | :--- |
| `PostgreSQL connection refused` | PostgreSQL service is stopped or credentials in `.env` are wrong | Verify PostgreSQL service is running on port 5432 and credentials match `DATABASE_URL`. |
| `Greenlet / asyncio error` | SQLAlchemy asyncio requires greenlet package | Ensure `greenlet>=3.0.0` is installed via `pip install greenlet`. |
| `Gemini API quota exceeded` | Free-tier Gemini quota limit reached | The system automatically switches to built-in deterministic compilers; no crash occurs. |
| `CORS Error in Browser` | Frontend port not listed in backend CORS origins | Ensure your frontend URL (e.g. `http://localhost:5173`) is listed in `CORS_ORIGINS` in `backend/app/config.py`. |
| `Vite build fails on Badges` | Named export mismatch | Verify all badges (`Badge`, `CategoryBadge`, `SentimentBadge`, `SourceBadge`, `StatusBadge`) are exported from `frontend/src/components/common/Badge.jsx`. |
| `Empty source results` | Query too specific or topic has no recent news | System gracefully reports 0 records collected and flags source status as `EMPTY` without failing. |
| `PDF download fails` | ReportLab storage folder missing | Backend automatically creates `STORAGE_DIR` (`./storage/reports`) on startup. |

---

## 18. Security Posture

1. **Zero Secret Exposure**: No API keys, credentials, or private tokens are embedded in frontend source code or transmitted to web browsers.
2. **Environment Isolation**: `.env` and `backend/.env` are strictly excluded from version control via `.gitignore`.
3. **Input Sanitization & Type Safety**: Pydantic v2 enforces schema validation on all inputs before execution.
4. **Parameterized SQL Queries**: All database transactions utilize SQLAlchemy ORM with parameterized arguments, preventing SQL injection vulnerabilities.
5. **Sanitized Error Responses**: Internal tracebacks are logged on the server; client-facing API responses return sanitized error descriptions.

---

## 19. Known Limitations

1. **Forecasting Requirement**: Linear regression forecasting requires at least 3 distinct chronological time points. If records are from a single date, forecasting is explicitly reported as `Unavailable` to avoid false projections.
2. **Social Media Quotas**: Reddit and YouTube APIs are subject to platform rate limits; open News/RSS feeds and dataset uploads are unlimited.
3. **Independent Sessions**: By design, conversational history is not maintained between separate queries.

---

## 20. Development Workflow

- **Modifying Analytics Algorithms**: Edit files in `backend/app/services/analytics/` (e.g. adjust VADER thresholds in `sentiment.py` or NMF components in `topics.py`).
- **Adding New Data Connectors**: Create a class inheriting from `BaseSourceConnector` in `backend/app/services/connectors/` and register it in `orchestrator.py`.
- **Modifying Database Schema**: Add columns to models in `backend/app/models/` and corresponding DTOs in `backend/app/schemas/`.
- **Updating Frontend Widgets**: Edit components in `frontend/src/components/dashboard/`.
- **Running Tests**: Run `pytest backend/tests/ -v` after any code modification.

---

## 21. Testing Guide

Run the complete 15-test automated backend test suite:
```bash
.venv\Scripts\python.exe -m pytest backend/tests/ -v
```

### Test Coverage Summary
- `test_api_endpoints.py`: Verifies `/health`, `/sources/health`, validation rules, and end-to-end background orchestration.
- `test_edge_cases.py`: Verifies 404 handlers, unsupported file rejection, empty file handling, dirty text sanitization, sparse topic/forecast handling, and heuristic compilers.
- `test_input_analyzer.py`: Verifies classification across `PRODUCT`, `POLICY`, `URL`, and `TOPIC`.
- `test_analytics_engine.py`: Verifies end-to-end NLP calculations across sentiment, emotions, topics, and trends.
- `test_pdf_builder.py`: Verifies vector PDF generation and disk serialization.

---

## 22. Production Deployment Guidelines

### Backend Deployment (e.g., Docker, AWS ECS, GCP Cloud Run, DigitalOcean)
- Expose port `8000`.
- Set production environment variables (`ENVIRONMENT="production"`, `DEBUG=False`).
- Provide managed PostgreSQL connection string in `DATABASE_URL`.
- Execute with production ASGI server:
  ```bash
  uvicorn main:app --app-dir backend --host 0.0.0.0 --port 8000 --workers 4
  ```

### Frontend Deployment (e.g., Vercel, Netlify, Cloudflare Pages, Nginx)
- Build optimized static production bundle:
  ```bash
  cd frontend
  npm run build
  ```
- Output directory: `frontend/dist/`.
- Set `VITE_API_BASE_URL` to the public URL of your backend service.
