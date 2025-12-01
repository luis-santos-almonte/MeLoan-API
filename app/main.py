from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import create_tables
from app.routes.loans import router as loans_router
from app.routes.amortization import router as amortization_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API for managing personal loans.",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION} in port: 8000")
    if settings.DEBUG:
        print("📊 Creating DB tables...")
        create_tables()

@app.on_event("shutdown")
async def shutdown_event():
    print("👋 Closing application")

app.include_router(loans_router)
app.include_router(amortization_router)

@app.get("/", tags=["root"])
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "healthy"}

@app.get("/api/test", tags=["test"])
async def test():
    return {
        "message": "API working correctly",
        "endpoints": {
            "loans": "/api/loans",
            "docs": "/docs"
        }
    }