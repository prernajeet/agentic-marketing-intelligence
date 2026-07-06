# Agentic Marketing Intelligence Platform

An enterprise-grade AI-powered marketing analytics platform using LangGraph, Google Gemini 2.5 Flash, PostgreSQL, FastAPI, Streamlit, and MLOps.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   User / Streamlit Dashboard                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                      FastAPI REST API                        │
│  /health  /workflows  /analytics  /predictions  /reports     │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│              LangGraph Workflow Engine                        │
│  planning → context → data_retrieval → validation →          │
│  feature_engineering → analytics → ml_strategy → decision →  │
│  training → evaluation → prediction → explainability →       │
│  simulation → business_insight → recommendation → reporting  │
└──────────────────────────┬──────────────────────────────────┘
                           │
       ┌───────────────────┼──────────────────┐
       │                   │                  │
┌──────▼──────┐  ┌────────▼────────┐  ┌──────▼───────┐
│ Gemini 2.5  │  │  Python ML/     │  │  PostgreSQL  │
│ Flash (LLM) │  │  Analytics      │  │  Database    │
└─────────────┘  └─────────────────┘  └──────────────┘
```

## Features

- 🤖 **AI Planning** — Gemini 2.5 Flash understands natural language queries and routes workflows
- 📊 **RFM Analysis** — Customer recency, frequency, and monetary scoring with 8 segment labels
- 🎯 **Customer Segmentation** — K-Means clustering with interpretable segment labels
- 🔴 **Churn Prediction** — XGBoost, LightGBM, RandomForest, GradientBoosting comparison
- 💰 **CLV Prediction** — Multi-model customer lifetime value regression
- 🔍 **Explainability** — SHAP values and feature importances per model
- 🎯 **What-If Simulation** — Parameter sensitivity analysis
- 📈 **Executive Reports** — AI-generated markdown reports saved to disk
- 🚀 **10-page Streamlit Dashboard** — Interactive analytics interface

## Quick Start

### Option 1: Docker (Recommended)

```bash
# 1. Clone the repository
git clone <repo_url>
cd agentic-marketing-intelligence

# 2. Set up environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 3. Launch all services
docker compose up --build

# 4. Verify API is running
curl http://localhost:8000/health

# 5. Access Streamlit Dashboard
# Open http://localhost:8501 in your browser

# 6. Generate sample data
docker exec marketing_api python data/raw/generate_data.py

# 7. Import data into PostgreSQL
curl -X POST http://localhost:8000/api/v1/data/import
```

### Option 2: Local Development

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment
cp .env.example .env
# Edit .env with your PostgreSQL URL and Gemini API key

# 4. Generate sample data
python data/raw/generate_data.py

# 5. Start the API
python app.py

# 6. Start the dashboard (new terminal)
streamlit run dashboard/streamlit_app.py
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check with DB status |
| POST | `/api/v1/workflows/run` | Run full LangGraph workflow |
| POST | `/api/v1/data/import` | Import CSV data to PostgreSQL |
| GET | `/api/v1/analytics/summary` | High-level analytics KPIs |
| POST | `/api/v1/predictions/churn` | Churn predictions |
| POST | `/api/v1/predictions/clv` | CLV predictions |
| POST | `/api/v1/simulations/what-if` | What-if simulation |
| GET | `/api/v1/reports/latest` | Latest executive report |

## Interactive API Docs

Once running, visit: http://localhost:8000/docs

## Streamlit Dashboard Pages

1. **Business Query** — Natural language interface to the full workflow
2. **Customer Analytics** — RFM segmentation and customer metrics
3. **Revenue Analytics** — Revenue trends and breakdowns
4. **Campaign Analytics** — Campaign funnel and performance
5. **Product Analytics** — Top products by revenue and units
6. **ML Results** — Model comparison with metrics table
7. **Predictions** — Churn and CLV predictions with visualizations
8. **Explainability** — SHAP values and feature importances
9. **What-If Simulation** — Interactive parameter adjustment
10. **Executive Report** — AI-generated report with download

## Environment Variables

| Variable | Description | Default |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | localhost/marketing_db |
| `GEMINI_API_KEY` | Google Gemini API key | (required for AI features) |
| `GEMINI_MODEL` | Gemini model name | gemini-2.5-flash |
| `API_PORT` | FastAPI port | 8000 |
| `API_DEBUG` | Enable debug mode | false |

## LangGraph Workflow Nodes

| Node | Role | Uses Gemini? |
|------|------|-------------|
| planning | Parse query, decide workflow path | ✅ Yes |
| context | Detect available data sources | No |
| data_retrieval | Load CSVs into state | No |
| validation | Validate data quality | No |
| feature_engineering | Build ML-ready features | No |
| analytics | RFM, segmentation, revenue, campaign | No |
| ml_strategy | Choose models and metrics | ✅ Yes |
| decision | Train or use existing champion | No |
| training | Train ML models | No |
| evaluation | Compare models, select champion | No |
| prediction | Churn and CLV predictions | No |
| explainability | SHAP values and importances | No |
| simulation | What-if parameter changes | No |
| business_insight | Generate data-driven insights | ✅ Yes |
| recommendation | Generate strategic actions | ✅ Yes |
| reporting | Write executive report | ✅ Yes |
| memory | Persist workflow history | No |

## Running Tests

```bash
pytest tests/ -v
```

## Project Structure

```
agentic-marketing-intelligence/
├── app.py                    # FastAPI entrypoint
├── dashboard/
│   ├── streamlit_app.py      # Main dashboard
│   └── pages/                # 10 Streamlit pages
├── graph/                    # LangGraph workflow
├── nodes/                    # 17 LangGraph nodes
├── analytics/                # RFM, segmentation, revenue, campaign, product
├── ml/                       # Churn, CLV, model registry, comparison
├── llm/                      # Gemini client
├── api/                      # FastAPI routes and schemas
├── database/                 # SQLAlchemy models, schema, loader
├── config/                   # Pydantic settings
├── visualizations/           # Plotly charts
├── mlops/                    # Model registry, versioning, monitoring
├── tests/                    # Unit and smoke tests
├── data/raw/                 # CSV data + generator
├── reports/                  # Generated executive reports
└── docker-compose.yml
```
