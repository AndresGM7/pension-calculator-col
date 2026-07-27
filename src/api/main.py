"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.settings import get_settings
from src.api.routes import pension

settings = get_settings()

app = FastAPI(
    title="Pension Calculator",
    description="Colombian pension calculator microservice — Ley 100/1993 + Ley 797/2003",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(pension.router, prefix="/api/v1/pension", tags=["pension"])


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "version": "0.1.0"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "pension-calculator",
        "version": "0.1.0",
        "docs": "/docs",
    }
