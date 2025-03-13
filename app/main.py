from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
import uvicorn
from app.config.database import Base, engine
from app.routers.api import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI
app = FastAPI(
    title="Coffee Quality API",
    description="API for managing coffee quality data from the Coffee Quality Institute",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api")

@app.get("/", tags=["Root"])
def read_root():
    """
    Root endpoint with API information
    """
    return {
        "message": "Welcome to the Coffee Quality API",
        "version": "1.0.0",
        "documentation": "/docs"
    }

@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}

# Ensure the correct port binding for Render
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Use Render-assigned PORT, default to 8000
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)