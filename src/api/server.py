"""
FastAPI Server Module.

This module provides the main FastAPI application with all routes
for the startup performance prediction system.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any, List

from .routes import domains, scenarios, portfolios, arguments, policies

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Startup Performance Prediction API",
    description="API for analyzing startup performance and predicting financial impact of events",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(domains.router, prefix="/api/v1/domains", tags=["domains"])
app.include_router(scenarios.router, prefix="/api/v1/scenarios", tags=["scenarios"])
app.include_router(portfolios.router, prefix="/api/v1/portfolios", tags=["portfolios"])
app.include_router(arguments.router, prefix="/api/v1/arguments", tags=["arguments"])
app.include_router(policies.router, prefix="/api/v1/policies", tags=["policies"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Startup Performance Prediction API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z"
    }


@app.get("/api/v1/status")
async def api_status():
    """API status endpoint."""
    return {
        "api_version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "domains": "/api/v1/domains",
            "scenarios": "/api/v1/scenarios",
            "portfolios": "/api/v1/portfolios",
            "arguments": "/api/v1/arguments",
            "policies": "/api/v1/policies"
        }
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "type": type(exc).__name__
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)








