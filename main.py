"""Main application entry point."""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from config.loader import settings
from utils.logger import setup_logger
from api.routes import router
from scheduler.manager import get_scheduler_manager

# Setup logger
logger = setup_logger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Meta Ad Campaign Automation",
    description="Automate Advantage+ Sales campaign creation and scheduling",
    version="1.0.0"
)

# Include API routes
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info("Starting Meta Ad Campaign Automation service...")
    logger.info(f"API running on {settings.api_host}:{settings.api_port}")
    logger.info(f"Log level: {settings.log_level}")

    # Start scheduler
    scheduler = get_scheduler_manager(data_dir=settings.data_dir)
    scheduler.start()
    logger.info("Scheduler started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("Shutting down Meta Ad Campaign Automation service...")

    # Shutdown scheduler
    scheduler = get_scheduler_manager(data_dir=settings.data_dir)
    scheduler.shutdown()
    logger.info("Scheduler shutdown successfully")


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "service": "Meta Ad Campaign Automation",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse(
        status_code=200,
        content={"status": "healthy"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
