from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from routes import auth, pairing, usage, prediction, notifications
from database import db
from services.ml_service import ml_service
from config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await db.connect()
    ml_service.load_models()
    print("Backend server starting...")
    yield
    # Shutdown
    await db.disconnect()
    print("Backend server shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(pairing.router, prefix=settings.API_V1_STR)
app.include_router(usage.router, prefix=settings.API_V1_STR)
app.include_router(prediction.router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "message": "Digital Fatigue Prediction System API",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected" if db.client else "disconnected",
        "ml_models": "loaded" if ml_service.is_loaded else "not loaded"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )