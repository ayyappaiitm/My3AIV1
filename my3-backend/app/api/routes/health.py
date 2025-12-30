from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from datetime import datetime
from sqlalchemy import text
from app.database.connection import engine
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    Tests database connection and returns service status.
    Returns 503 if database is unavailable.
    """
    try:
        # Test database connection
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.scalar()  # Verify query executed successfully
        
        database_status = "connected"
        overall_status = "healthy"
        http_status = status.HTTP_200_OK
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}", exc_info=True)
        database_status = "disconnected"
        overall_status = "unhealthy"
        http_status = status.HTTP_503_SERVICE_UNAVAILABLE
    
    response_data = {
        "status": overall_status,
        "database": database_status,
        "timestamp": datetime.utcnow().isoformat(),
        "service": "my3-backend"
    }
    
    return JSONResponse(
        status_code=http_status,
        content=response_data
    )


