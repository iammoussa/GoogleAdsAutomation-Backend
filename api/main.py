"""
FastAPI Application - API REST per Dashboard
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import uvicorn

from database.database import get_db, init_db
from database.models import CampaignMetric, Alert, ProposedAction, ActionLog
from config.settings import settings
from utils.logger import get_logger

# Import routes
from api.routes import campaigns, actions, optimizations, stats, health

logger = get_logger(__name__)

# Crea app
app = FastAPI(
    title="Google Ads Automation API",
    description="API REST per gestione automazione campagne Google Ads",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS (permetti richieste da Flutter app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In produzione: specifica domini esatti
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(campaigns.router, prefix="/api/campaigns", tags=["Campaigns"])
app.include_router(actions.router, prefix="/api/actions", tags=["Actions"])
app.include_router(optimizations.router, prefix="/api/optimizations", tags=["Optimizations"])
app.include_router(stats.router, prefix="/api/stats", tags=["Stats"])
app.include_router(health.router, prefix="/api", tags=["Health"])

@app.get("/")
async def root():
    return {"message": "AdOptimizer AI Backend is running"}


@app.on_event("startup")
async def startup_event():
    """
    Eseguito all'avvio del server
    """
    logger.info("🚀 Avvio FastAPI server...")
    logger.info(f"📝 Environment: {settings.LOG_LEVEL}")
    logger.info(f"📊 Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'local'}")
    
    # Verifica database
    try:
        init_db()
        logger.info("✅ Database connesso")
    except Exception as e:
        logger.error(f"❌ Errore connessione database: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Eseguito allo shutdown del server
    """
    logger.info("🛑 Shutdown FastAPI server")


@app.get("/")
async def root():
    """
    Root endpoint - Health check
    """
    return {
        "service": "Google Ads Automation API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check completo
    """
    try:
        # Test database
        db.execute("SELECT 1")
        
        # Conta records recenti
        cutoff = datetime.now() - timedelta(hours=24)
        recent_metrics = db.query(CampaignMetric).filter(
            CampaignMetric.timestamp >= cutoff
        ).count()
        
        pending_actions = db.query(ProposedAction).filter(
            ProposedAction.status == 'PENDING'
        ).count()
        
        return {
            "status": "healthy",
            "database": "connected",
            "recent_metrics_24h": recent_metrics,
            "pending_actions": pending_actions,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats/summary")
async def get_summary_stats(db: Session = Depends(get_db)):
    """
    Statistiche generali del sistema
    """
    try:
        # Total campagne
        total_campaigns = db.query(CampaignMetric.campaign_id).distinct().count()
        
        # Metriche ultime 24h
        cutoff_24h = datetime.now() - timedelta(hours=24)
        metrics_24h = db.query(CampaignMetric).filter(
            CampaignMetric.timestamp >= cutoff_24h
        ).all()
        
        total_spend_24h = sum(float(m.cost) for m in metrics_24h)
        total_conversions_24h = sum(float(m.conversions) for m in metrics_24h)
        total_conv_value_24h = sum(float(m.conv_value) for m in metrics_24h)
        
        # Alert attivi
        active_alerts = db.query(Alert).filter(
            Alert.resolved == False
        ).count()
        
        # Azioni pending
        pending_actions = db.query(ProposedAction).filter(
            ProposedAction.status == 'PENDING'
        ).count()
        
        # Azioni eseguite ultima settimana
        cutoff_7d = datetime.now() - timedelta(days=7)
        executed_actions_7d = db.query(ActionLog).filter(
            ActionLog.executed_at >= cutoff_7d,
            ActionLog.status == 'SUCCESS'
        ).count()
        
        return {
            "total_campaigns": total_campaigns,
            "last_24h": {
                "spend": round(total_spend_24h, 2),
                "conversions": round(total_conversions_24h, 1),
                "conv_value": round(total_conv_value_24h, 2),
                "roas": round(total_conv_value_24h / total_spend_24h, 2) if total_spend_24h > 0 else 0
            },
            "active_alerts": active_alerts,
            "pending_actions": pending_actions,
            "executed_actions_last_7d": executed_actions_7d,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Errore stats summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Handler globale per eccezioni non gestite
    """
    logger.error(f"❌ Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )


# Entry point
if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )