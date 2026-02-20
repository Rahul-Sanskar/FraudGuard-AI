"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.model_manager import model_manager
from app.api.endpoints import router
from app.models.database import Base
from app.db.session import engine

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    setup_logging()
    logger.info("Starting FraudGuard AI Platform")
    
    # Initialize model manager (checks model availability)
    logger.info("Initializing model manager...")
    status = model_manager.get_status()
    logger.info(f"Model status: {status['available_models']}/{status['total_models']} models available")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    
    logger.info("✅ FraudGuard AI Platform ready")
    
    yield
    
    # Shutdown
    logger.info("Shutting down FraudGuard AI Platform")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "FraudGuard AI - Fraud Detection Platform",
        "version": settings.VERSION,
        "docs": "/docs"
    }
