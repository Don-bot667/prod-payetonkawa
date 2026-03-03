import os
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from .database import engine, Base, SessionLocal
from .routes import router
from .logging_config import logger, LoggingMiddleware

Base.metadata.create_all(bind=engine)

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:4321"
).split(",")

app = FastAPI(
    title="PayeTonKawa - API Commandes",
    version="1.0.0"
)

app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API Commandes de PayeTonKawa"}


@app.get("/health", tags=["Health"])
def health_check():
    """Vérifie que l'API et la base de données sont opérationnelles."""
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        db_status = "connected"
    except Exception as e:
        logger.error(f"Healthcheck DB failed: {e}")
        db_status = f"error: {str(e)}"

    status = "healthy" if db_status == "connected" else "unhealthy"
    return {
        "status": status,
        "service": "api-commandes",
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
    }
