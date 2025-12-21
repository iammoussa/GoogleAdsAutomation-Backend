"""
Routes per gestione ottimizzazioni
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime

from database.database import get_db
from database.models import ProposedAction, ActionLog
from agents.executor import CampaignExecutor
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("")
async def get_optimizations(
    campaign_id: Optional[int] = Query(None, description="Filter by campaign"),
    status: Optional[str] = Query(None, description="Filter by status (PENDING, APPROVED, REJECTED, APPLIED)"),
    priority: Optional[str] = Query(None, description="Filter by priority (HIGH, MEDIUM, LOW)"),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Get all optimizations (ProposedActions)
    """
    try:
        query = db.query(ProposedAction)
        
        if campaign_id:
            query = query.filter(ProposedAction.campaign_id == campaign_id)
        
        if status:
            query = query.filter(ProposedAction.status == status.upper())
        
        if priority:
            query = query.filter(ProposedAction.priority == priority.upper())
        
        optimizations = query.order_by(
            ProposedAction.priority.desc(),
            ProposedAction.created_at.desc()
        ).limit(limit).all()
        
        logger.success(f"✅ Found {len(optimizations)} optimizations")
        
        return {
            "count": len(optimizations),
            "optimizations": [opt.to_dict() for opt in optimizations]
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting optimizations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/count")
async def get_optimizations_count(
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db)
):
    """
    Get count of optimizations by status
    """
    try:
        query = db.query(ProposedAction)
        
        if status:
            query = query.filter(ProposedAction.status == status.upper())
        
        count = query.count()
        
        return {
            "count": count,
            "status": status or "ALL"
        }
        
    except Exception as e:
        logger.error(f"❌ Error counting optimizations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{optimization_id}/apply")
async def apply_optimization(
    optimization_id: int,
    db: Session = Depends(get_db)
):
    """
    Apply an optimization (approve and execute)
    """
    try:
        # Find optimization
        optimization = db.query(ProposedAction).filter(
            ProposedAction.id == optimization_id
        ).first()
        
        if not optimization:
            raise HTTPException(status_code=404, detail=f"Optimization {optimization_id} not found")
        
        if optimization.status != 'PENDING':
            raise HTTPException(
                status_code=400,
                detail=f"Optimization is not pending (current status: {optimization.status})"
            )
        
        # Approve
        optimization.status = 'APPROVED'
        optimization.approved_at = datetime.now()
        optimization.approved_by = "user@dashboard"
        db.commit()
        
        logger.info(f"✅ Optimization {optimization_id} APPROVED")
        
        # Validate optimization has required data
        if optimization.action_type in ['INCREASE_BUDGET', 'DECREASE_BUDGET', 'CHANGE_BUDGET']:
            target = optimization.target or {}
            if not target.get('new_budget_micros'):
                raise HTTPException(
                    status_code=400,
                    detail="Optimization missing required field: new_budget_micros in target"
                )
        
        # Execute
        try:
            executor = CampaignExecutor()
            result = executor.execute_action(optimization)
            
            if result.get('status') == 'SUCCESS':
                optimization.status = 'APPLIED'
                optimization.executed_at = datetime.now()
                
                # Log execution
                log = ActionLog(
                    action_id=optimization.id,
                    campaign_id=optimization.campaign_id,
                    action_type=optimization.action_type,
                    status='SUCCESS',
                    executed_at=datetime.now(),
                    details=result.get('data', {}),  # Add details field
                    api_response=result.get('data', {})
                )
                db.add(log)
                db.commit()
                
                logger.success(f"✅ Optimization {optimization_id} APPLIED successfully")
                
                return {
                    "success": True,
                    "optimization_id": optimization_id,
                    "status": "APPLIED",
                    "message": "Optimization applied successfully",
                    "result": result
                }
            else:
                # Execution failed
                optimization.status = 'FAILED'
                
                log = ActionLog(
                    action_id=optimization.id,
                    campaign_id=optimization.campaign_id,
                    action_type=optimization.action_type,
                    status='FAILED',
                    executed_at=datetime.now(),
                    details={},  # Add details field
                    error_message=result.get('reason') or result.get('error')
                )
                db.add(log)
                db.commit()
                
                logger.error(f"❌ Optimization {optimization_id} FAILED: {result.get('reason')}")
                
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to apply optimization: {result.get('reason') or result.get('error')}"
                )
                
        except Exception as e:
            logger.error(f"❌ Error executing optimization {optimization_id}: {e}")
            optimization.status = 'FAILED'
            db.commit()
            raise HTTPException(status_code=500, detail=str(e))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error applying optimization: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{optimization_id}/dismiss")
async def dismiss_optimization(
    optimization_id: int,
    db: Session = Depends(get_db)
):
    """
    Dismiss/reject an optimization
    """
    try:
        optimization = db.query(ProposedAction).filter(
            ProposedAction.id == optimization_id
        ).first()
        
        if not optimization:
            raise HTTPException(status_code=404, detail=f"Optimization {optimization_id} not found")
        
        if optimization.status != 'PENDING':
            raise HTTPException(
                status_code=400,
                detail=f"Optimization is not pending (current status: {optimization.status})"
            )
        
        optimization.status = 'DISMISSED'
        db.commit()
        
        logger.info(f"🚫 Optimization {optimization_id} DISMISSED")
        
        return {
            "success": True,
            "optimization_id": optimization_id,
            "status": "DISMISSED",
            "message": "Optimization dismissed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error dismissing optimization: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{optimization_id}")
async def get_optimization_detail(
    optimization_id: int,
    include_logs: bool = Query(False, description="Include execution logs"),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific optimization
    """
    try:
        optimization = db.query(ProposedAction).filter(
            ProposedAction.id == optimization_id
        ).first()
        
        if not optimization:
            raise HTTPException(status_code=404, detail=f"Optimization {optimization_id} not found")
        
        opt_dict = optimization.to_dict()
        
        if include_logs:
            logs = db.query(ActionLog).filter(
                ActionLog.action_id == optimization_id
            ).all()
            opt_dict['logs'] = [log.to_dict() for log in logs]
        
        return opt_dict
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting optimization detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))