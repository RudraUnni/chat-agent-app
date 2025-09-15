"""
Health check endpoints with OpenRouter API validation.
"""
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
import logging
import redis.asyncio as redis
from app.services.llm.openrouter_client import get_openrouter_client
from app.core.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/health", tags=["health"])
settings = get_settings()


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """
    Comprehensive health check including:
    - OpenRouter API key validity
    - OpenRouter connectivity 
    - Redis connectivity
    - Basic service status
    """
    health_status = {
        "status": "healthy",
        "services": {},
        "timestamp": __import__('time').time()
    }
    
    overall_healthy = True
    
    # Check OpenRouter connectivity and API key validity
    try:
        client = get_openrouter_client()
        openrouter_health = await client.health_check()
        health_status["services"]["openrouter"] = openrouter_health
        
        if not openrouter_health.get("api_key_valid", False):
            overall_healthy = False
            
    except Exception as e:
        logger.error(f"OpenRouter health check failed: {e}")
        health_status["services"]["openrouter"] = {
            "status": "unhealthy",
            "error": str(e),
            "api_key_valid": False
        }
        overall_healthy = False
    
    # Check Redis connectivity
    try:
        redis_host = getattr(settings, 'redis_host', 'localhost')
        redis_port = int(getattr(settings, 'redis_port', 6379))
        redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        
        # Test Redis connection
        await redis_client.ping()
        health_status["services"]["redis"] = {
            "status": "healthy",
            "host": redis_host,
            "port": redis_port
        }
        await redis_client.close()
        
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        health_status["services"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        overall_healthy = False
    
    # Check database connectivity (basic check)
    try:
        from app.database.connection import engine
        async with engine.begin() as conn:
            await conn.execute(__import__('sqlalchemy').text("SELECT 1"))
        
        health_status["services"]["database"] = {
            "status": "healthy",
            "type": "postgresql"
        }
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["services"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        overall_healthy = False
    
    # Set overall status
    if not overall_healthy:
        health_status["status"] = "unhealthy"
    
    # Return appropriate HTTP status
    if health_status["status"] == "unhealthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=health_status
        )
    
    return health_status


@router.get("/openrouter")
async def openrouter_health() -> Dict[str, Any]:
    """Detailed OpenRouter API health check"""
    try:
        client = get_openrouter_client()
        health_result = await client.health_check()
        
        # Add additional OpenRouter-specific checks
        try:
            models = await client.list_models()
            health_result["available_models"] = len(models)
            health_result["models_sample"] = [m.get("id", "unknown") for m in models[:3]]
        except Exception as e:
            health_result["models_error"] = str(e)
        
        return health_result
        
    except Exception as e:
        logger.error(f"OpenRouter detailed health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "error": str(e),
                "api_key_valid": False
            }
        )


@router.get("/redis")
async def redis_health() -> Dict[str, Any]:
    """Detailed Redis health check"""
    try:
        redis_host = getattr(settings, 'redis_host', 'localhost')
        redis_port = int(getattr(settings, 'redis_port', 6379))
        redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        
        # Test basic operations
        await redis_client.ping()
        info = await redis_client.info()
        
        result = {
            "status": "healthy",
            "host": redis_host,
            "port": redis_port,
            "version": info.get("redis_version", "unknown"),
            "connected_clients": info.get("connected_clients", 0),
            "used_memory_human": info.get("used_memory_human", "unknown")
        }
        
        await redis_client.close()
        return result
        
    except Exception as e:
        logger.error(f"Redis detailed health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "error": str(e)
            }
        )


@router.get("/database")
async def database_health() -> Dict[str, Any]:
    """Detailed database health check"""
    try:
        from app.database.connection import engine
        
        async with engine.begin() as conn:
            # Test basic query
            result = await conn.execute(__import__('sqlalchemy').text("SELECT version()"))
            version = result.scalar()
            
            # Test table existence
            tables_result = await conn.execute(__import__('sqlalchemy').text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = [row[0] for row in tables_result.fetchall()]
        
        return {
            "status": "healthy",
            "type": "postgresql",
            "version": version,
            "tables": tables,
            "table_count": len(tables)
        }
        
    except Exception as e:
        logger.error(f"Database detailed health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "error": str(e)
            }
        )