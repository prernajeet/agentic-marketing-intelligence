from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from api.routes import health, workflows, data, analytics, predictions, simulations, reports
from database.connection import engine
from database.models import Base
from config.settings import settings
from utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Agentic Marketing Intelligence API")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.warning(f"Database setup warning: {e}")
    yield
    # Shutdown
    logger.info("Shutting down API")


app = FastAPI(
    title="Agentic Marketing Intelligence Platform",
    description="Enterprise AI marketing analytics with LangGraph, Gemini, and ML",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health.router)
app.include_router(workflows.router)
app.include_router(data.router)
app.include_router(analytics.router)
app.include_router(predictions.router)
app.include_router(simulations.router)
app.include_router(reports.router)


@app.get("/")
def root():
    return {
        "name": "Agentic Marketing Intelligence Platform",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug,
    )
