# Agentic AI-Powered Marketing Intelligence & Decision Support Platform

An enterprise-inspired **Agentic AI** platform that automates the complete
marketing analytics lifecycle: planning, data retrieval, validation,
feature engineering, analytics, ML model training/evaluation/selection,
prediction, explainability, simulation, business insight generation,
recommendations, and executive reporting — orchestrated end-to-end via
**LangGraph**.

This is not a dashboard or a notebook. It is a modular, production-style
decision-support system.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Backend API | FastAPI |
| Workflow Orchestration | LangGraph (Nodes, not Agents) |
| LLM Reasoning | Google Gemini 2.5 Flash |
| Database | PostgreSQL + SQLAlchemy |
| Machine Learning | Scikit-learn, XGBoost, LightGBM, CatBoost, HistGradientBoosting, Random Forest, Logistic Regression, Decision Tree, Extra Trees, AdaBoost, KNN, SVM, KMeans |
| Explainability | SHAP |
| Visualization | Plotly |
| MLOps | Model Registry, Versioning, Monitoring, Pipeline (MLflow) |
| Containerization | Docker & Docker Compose |

## Project Structure

```
agentic-marketing-intelligence/
├── app.py                  # Streamlit entrypoint
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── config/                 # Centralized settings, logging, constants
├── database/                # PostgreSQL connection, schema, queries
├── api/                     # FastAPI endpoints & schemas
├── graph/                   # LangGraph workflow definition, state, routing
├── nodes/                   # Individual LangGraph node implementations
├── analytics/                # Business analytics (RFM, KPIs, segmentation)
├── ml/                       # Training, evaluation, prediction pipelines
├── llm/                      # Gemini prompts, insights, recommendations
├── dashboard/                 # Streamlit pages
├── visualizations/             # Plotly charts & KPI components
├── mlops/                      # Model registry, versioning, monitoring
├── utils/                       # Shared helpers
├── reports/                      # Generated executive reports
├── tests/                        # Unit & integration tests
└── data/
    ├── raw/
    ├── processed/
    └── exports/
```

## LangGraph Node Architecture

Every node has **one responsibility**. The **Planning Node** decides which
downstream nodes actually need to run for a given request — the workflow
does not blindly execute the full pipeline every time.

1. **Planning Node** — interprets the goal, builds an execution plan
2. **Context Node** — classifies the request (customer / campaign / revenue / product / marketing)
3. **Data Retrieval Node** — loads only the required datasets
4. **Data Validation Node** — checks missing values, duplicates, outliers
5. **Feature Engineering Node** — builds ML-ready features
6. **Analytics Node** — KPIs, RFM, segmentation
7. **ML Strategy Node** — chooses classification / regression / clustering
8. **Model Training Node** — trains multiple candidate models
9. **Model Evaluation Node** — compares via Accuracy, Precision, Recall, F1, ROC-AUC, CV
10. **Decision Node** — selects & justifies the best model
11. **Prediction Node** — churn, CLV, RFM, segmentation outputs
12. **Explainability Node** — SHAP & feature importance
13. **Simulation Node** — what-if business scenarios
14. **Business Insight Node** — Gemini translates technical results to business language
15. **Recommendation Node** — strategic recommendations with confidence/ROI
16. **Reporting Node** — executive report generation
17. **Memory Node** — maintains workflow state across the graph

Gemini is used **only** for reasoning (planning, insights, recommendations,
report writing, NLU) — never for data cleaning, SQL, ML, or predictions.

## Getting Started

```bash
# 1. Clone and enter the project
cd agentic-marketing-intelligence

# 2. Copy environment template and fill in real values
cp .env.example .env

# 3. Install dependencies (local dev)
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Run with Docker Compose (recommended)
docker-compose up --build
```

Services once running:

- FastAPI backend → `http://localhost:8000`
- Streamlit dashboard → `http://localhost:8501`
- PostgreSQL → `localhost:5432`

## Configuration

All configuration is environment-driven via `config/settings.py`, which
reads from `.env`. No credentials are ever hardcoded in source code.

## Status

🚧 Scaffolding phase — `config/` module complete (settings, logging,
constants). Next steps: `database/`, `graph/` (LangGraph state + workflow),
then `nodes/` implementations one node at a time.
