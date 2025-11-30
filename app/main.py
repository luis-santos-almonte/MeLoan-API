from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import create_tables

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Sistema de gestión de préstamos con precisión bancaria",
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
    print(f"🚀 Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")
    if settings.DEBUG:
        print("📊 Creando tablas de BD...")
        create_tables()

@app.on_event("shutdown")
async def shutdown_event():
    print("👋 Cerrando aplicación")


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
        "message": "API funcionando correctamente",
        "endpoints": {
            "loans": "/api/loans",
            "docs": "/docs"
        }
    }