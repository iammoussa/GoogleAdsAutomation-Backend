"""
Health Router - Health checks and system status
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from database.database import get_db
from database.models import CampaignMetric, ProposedAction
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint
    
    **Returns:**
    - System status
    - Database connectivity
    - Recent activity metrics
    """
    try:
        # Test database connection
        db.execute("SELECT 1")
        
        # Count recent metrics (last 24h)
        cutoff = datetime.now() - timedelta(hours=24)
        recent_metrics = db.query(CampaignMetric).filter(
            CampaignMetric.timestamp >= cutoff
        ).count()
        
        # Count pending actions
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
        raise HTTPException(
            status_code=500,
            detail={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )