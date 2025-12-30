from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time
from app.config import settings
from app.api.routes import auth, chat, recipients, health
from app.database.connection import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="My3 API",
    description="AI-powered personal relationship and gifting concierge",
    version="0.1.0"
)

# CORS middleware - Allow all origins in development for easier debugging
cors_origins = settings.cors_origins_list
if settings.environment == "development":
    # In development, allow all localhost ports
    cors_origins = ["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"]
    logger.info(f"Development mode: Using permissive CORS origins: {cors_origins}")
else:
    logger.info(f"Production mode: CORS origins configured: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log incoming request
    logger.info(f"→ {request.method} {request.url.path}")
    
    response = await call_next(request)
    duration = time.time() - start_time
    
    logger.info(f"← {request.method} {request.url.path} - {response.status_code} ({duration:.3f}s)")
    
    return response

# Include routers
# Note: Routers already have prefixes defined, so we don't add them here
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(recipients.router)
app.include_router(health.router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {"message": "My3 API - Your AI Gift Concierge"}


# Startup event
@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}", exc_info=True)
        # Don't raise - allow app to start even if DB init fails
        # (migrations should handle this in production)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    import traceback
    error_trace = traceback.format_exc()
    logger.error(f"Unhandled exception: {exc}\n{error_trace}", exc_info=True)
    
    # In development, return more details
    if settings.environment == "development":
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "error": str(exc),
                "type": type(exc).__name__
            }
        )
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

