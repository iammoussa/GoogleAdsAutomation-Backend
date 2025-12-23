"""
FastAPI Application - API REST per Dashboard
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import uvicorn
import threading

from database.database import get_db, init_db
from database.models import CampaignMetric, Alert, ProposedAction, ActionLog
from config.settings import settings
from utils.logger import get_logger

# Import routes
from api.routes import campaigns, actions, optimizations, stats, health

# Import scheduler components
from apscheduler.schedulers.background import BackgroundScheduler
from agents.monitor import CampaignMonitor
from agents.analyzer import CampaignAnalyzer

logger = get_logger(__name__)

# Global scheduler instance
scheduler = None


def run_monitoring_cycle():
    """Run monitoring and analysis cycle"""
    try:
        logger.info("🔄 Starting monitoring cycle...")
        
        # Initialize agents
        monitor = CampaignMonitor()
        analyzer = CampaignAnalyzer()
        
        # Run monitoring (saves to database automatically)
        result = monitor.run()
        logger.info(f"✅ Monitoring completed: {result['campaigns_count']} campaigns, {result['alerts_count']} alerts")
        
        # Run analysis (generates AI recommendations)
        logger.info("🤖 Starting AI analysis...")
        analysis_results = analyzer.analyze_all_campaigns()
        
        # Count optimizations generated
        total_optimizations = sum(len(r.get('proposed_actions', [])) for r in analysis_results)
        logger.info(f"✅ Analysis completed: {total_optimizations} recommendations generated")
        
    except Exception as e:
        logger.error(f"❌ Error in monitoring cycle: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        logger.error(f"❌ Error in monitoring cycle: {e}")
        import traceback
        traceback.print_exc()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    # STARTUP
    logger.info("🚀 Avvio FastAPI server...")
    logger.info(f"📝 Environment: {settings.LOG_LEVEL}")
    logger.info(f"📊 Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'local'}")
    
    # Initialize database
    try:
        init_db()
        logger.info("✅ Database connesso")
    except Exception as e:
        logger.error(f"❌ Errore connessione database: {e}")
    
    # Start scheduler
    global scheduler
    scheduler = BackgroundScheduler()
    
    # Schedule monitoring every 6 hours
    scheduler.add_job(
        run_monitoring_cycle,
        'interval',
        hours=6,
        id='monitoring_cycle',
        name='Campaign Monitoring Cycle',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("✅ Scheduler started - monitoring every 6 hours")
    
    # Run initial monitoring cycle in background
    logger.info("🔄 Running initial monitoring cycle...")
    threading.Thread(target=run_monitoring_cycle, daemon=True).start()
    
    yield
    
    # SHUTDOWN
    logger.info("🛑 Shutdown FastAPI server")
    if scheduler:
        scheduler.shutdown()
        logger.info("✅ Scheduler stopped")


# Crea app with lifespan
app = FastAPI(
    title="Google Ads Automation API",
    description="API REST per gestione automazione campagne Google Ads",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
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
    """Root endpoint"""
    return {
        "message": "AdOptimizer AI Backend is running",
        "service": "Google Ads Automation API",
        "version": "1.0.0",
        "status": "running",
        "scheduler_status": "running" if scheduler and scheduler.running else "stopped",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check completo"""
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        
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
            "scheduler": "running" if scheduler and scheduler.running else "stopped",
            "recent_metrics_24h": recent_metrics,
            "pending_actions": pending_actions,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats/summary")
async def get_summary_stats(db: Session = Depends(get_db)):
    """Statistiche generali del sistema"""
    try:
        total_campaigns = db.query(CampaignMetric.campaign_id).distinct().count()
        
        cutoff_24h = datetime.now() - timedelta(hours=24)
        metrics_24h = db.query(CampaignMetric).filter(
            CampaignMetric.timestamp >= cutoff_24h
        ).all()
        
        total_spend_24h = sum(float(m.cost) for m in metrics_24h)
        total_conversions_24h = sum(float(m.conversions) for m in metrics_24h)
        total_conv_value_24h = sum(float(m.conv_value) for m in metrics_24h)
        
        active_alerts = db.query(Alert).filter(
            Alert.resolved == False
        ).count()
        
        pending_actions = db.query(ProposedAction).filter(
            ProposedAction.status == 'PENDING'
        ).count()
        
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
    """Handler globale per eccezioni non gestite"""
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
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )