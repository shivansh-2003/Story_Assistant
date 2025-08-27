# main.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import asyncio
from datetime import datetime
import uvicorn

from config.settings import settings
from config.database_config import init_database, init_supabase_schema
from api.routes import router
from services.vector_service import get_vector_service
from services.llm_service import get_llm_service
from services.image_service import get_image_service

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Application lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - handles startup and shutdown"""
    logger.info("Starting Story Assistant application...")
    
    try:
        # Initialize database
        logger.info("Initializing database...")
        await init_database()
        
        # Initialize services
        logger.info("Initializing vector service...")
        vector_service = await get_vector_service()
        
        logger.info("Initializing LLM service...")
        llm_service = await get_llm_service()
        
        logger.info("Initializing image service...")
        image_service = await get_image_service()
        
        # Verify all services are healthy
        logger.info("Performing health checks...")
        
        vector_health = await vector_service.health_check()
        if vector_health.get("status") != "healthy":
            logger.warning(f"Vector service health check failed: {vector_health}")
        
        llm_health = await llm_service.health_check()
        if llm_health.get("service_status") not in ["healthy", "degraded"]:
            logger.warning(f"LLM service health check failed: {llm_health}")
        
        image_health = await image_service.health_check()
        if image_health.get("service_status") != "healthy":
            logger.warning(f"Image service health check failed: {image_health}")
        
        logger.info("✅ Story Assistant application started successfully!")
        
        yield  # Application runs here
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    finally:
        # Cleanup on shutdown
        logger.info("Shutting down Story Assistant application...")
        
        # Perform any necessary cleanup
        # Services will handle their own cleanup
        
        logger.info("✅ Application shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="Story Assistant API",
    description="AI-powered story generation and writing assistant with multi-agent orchestration and Gemini Vision analysis",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,  # Disable docs in production
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.debug else ["yourdomain.com", "*.yourdomain.com"]
)

# Custom middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests"""
    start_time = datetime.utcnow()
    
    # Log request
    logger.info(f"📥 {request.method} {request.url}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = (datetime.utcnow() - start_time).total_seconds()
    logger.info(f"📤 {request.method} {request.url} - {response.status_code} ({process_time:.3f}s)")
    
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# HTTP exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent format"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Include API routes
app.include_router(router, prefix="/api/v1")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with basic application info"""
    return {
        "name": "Story Assistant API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "docs": "/docs" if settings.debug else "Documentation not available",
        "health": "/api/v1/health",
        "features": [
            "Multi-Agent Story Generation",
            "Vector-Based Context Management", 
            "LLM Integration (Groq)",
            "Gemini Vision Analysis & Guidance"
        ]
    }

# Health check endpoint (public)
@app.get("/health")
async def public_health_check():
    """Public health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": [
            "Database",
            "Vector Service", 
            "LLM Service (Groq)",
            "Gemini Vision Service"
        ]
    }







# CLI commands for development
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Story Assistant API Server")
    parser.add_argument("--host", default=settings.host, help="Host to bind to")
    parser.add_argument("--port", type=int, default=settings.port, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes")
    parser.add_argument("--log-level", default="info", help="Log level")
    
    args = parser.parse_args()
    
    # Development server
    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers if not args.reload else 1,
        log_level=args.log_level,
        access_log=True
    )