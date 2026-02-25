from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Backend server starting...")
    
    try:
        from src.database import db
        await db.connect()
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("⚠️ Continuing without database for testing")
    
    try:
        from src.services.ml_service import ml_service
        ml_service.load_models()
        print("✅ ML models loaded")
    except Exception as e:
        print(f"⚠️ Failed to load ML models: {e}")
        print("   Note: Run 'python data_science/train_models.py' to train models")
    
    yield
    
    # Shutdown
    try:
        from src.database import db
        await db.disconnect()
        print("✅ Database connection closed")
    except:
        pass
    print("🔴 Backend server shutting down...")

# Create app
app = FastAPI(
    title="Digital Fatigue Guard",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from src.routes.auth import router as auth_router
from src.routes.pairing import router as pairing_router
from src.routes.usage import router as usage_router
from src.routes.prediction import router as prediction_router
# After including routers, add:
print(f"✅ Routers loaded: auth, pairing, usage, prediction")

app.include_router(auth_router, prefix="/api/v1")
app.include_router(pairing_router, prefix="/api/v1")
app.include_router(usage_router, prefix="/api/v1")
app.include_router(prediction_router, prefix="/api/v1")

# Basic routes
@app.get("/")
async def root():
    return {
        "message": "Digital Fatigue Prediction System API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    try:
        from src.database import db
        db_status = "healthy" if db.client else "disconnected"
    except:
        db_status = "unknown"
    
    try:
        from src.services.ml_service import ml_service
        ml_status = "loaded" if hasattr(ml_service, 'is_loaded') and ml_service.is_loaded else "not loaded"
    except:
        ml_status = "unknown"
    
    return {
        "status": "running",
        "database": db_status,
        "ml_models": ml_status,
        "environment": "development"
    }

@app.get("/config")
async def show_config():
    """Show current configuration (without sensitive data)"""
    from src.config import settings
    
    mongodb_url = settings.MONGODB_URL
    if "@" in mongodb_url:
        # Hide credentials
        parts = mongodb_url.split("@")
        mongodb_url = f"mongodb://***:***@{parts[1]}" if len(parts) > 1 else "***"
    
    return {
        "project_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database_name": settings.DATABASE_NAME,
        "mongodb_url": mongodb_url,
        "jwt_algorithm": settings.ALGORITHM,
        "token_expiry_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )