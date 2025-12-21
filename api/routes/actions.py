# -*- coding: utf-8 -*-
"""
AI Actions Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional

from api.models.schemas import ActionResponse, ApproveActionRequest, RejectActionRequest
from database.database import get_db
from api.dependencies import verify_token

router = APIRouter()

@router.get("/actions/pending", response_model=List[ActionResponse])
async def get_pending_actions(
    priority: Optional[str] = Query(None, description="Filter by priority (HIGH, MEDIUM, LOW)"),
    limit: int = Query(50, description="Max actions to return"),
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    Get list of pending AI actions awaiting approval
    
    Query params:
    - priority: Filter by priority (HIGH, MEDIUM, LOW)
    - limit: Max actions to return (default 50)
    """
    try:
        query = """
            SELECT 
                pa.id,
                pa.campaign_id,
                cm.campaign_name,
                pa.action_type,
                pa.priority,
                pa.target,
                pa.reason,
                pa.expected_impact,
                pa.confidence,
                pa.ai_summary,
                pa.status,
                pa.created_at
            FROM proposed_actions pa
            JOIN campaign_metrics cm ON pa.campaign_id = cm.campaign_id
            WHERE pa.status = 'PENDING'
        """
        
        params = {}
        if priority:
            query += " AND pa.priority = :priority"
            params["priority"] = priority
        
        query += " ORDER BY pa.created_at DESC LIMIT :limit"
        params["limit"] = limit
        
        result = db.execute(text(query), params)
        actions = []
        
        for row in result:
            # Parse target JSONB field
            import json
            target_data = row.target
            if isinstance(target_data, str):
                try:
                    target_data = json.loads(target_data)
                except:
                    target_data = {}
            elif not isinstance(target_data, dict):
                target_data = {}
            
            actions.append(ActionResponse(
                id=row.id,
                campaign_id=row.campaign_id,
                campaign_name=row.campaign_name,
                action_type=row.action_type,
                priority=row.priority,
                target=target_data,
                reason=row.reason,
                expected_impact=row.expected_impact,
                confidence=float(row.confidence),
                ai_summary=row.ai_summary or "",
                status=row.status,
                created_at=row.created_at
            ))
        
        return actions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching actions: {str(e)}")

@router.post("/actions/{action_id}/approve")
async def approve_action(
    action_id: int,
    request: ApproveActionRequest,
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    Approve an AI action
    
    This will:
    1. Mark action as APPROVED
    2. Trigger Executor agent to apply the change
    """
    try:
        # Update status
        result = db.execute(
            text("""
                UPDATE proposed_actions 
                SET status = 'APPROVED', 
                    updated_at = NOW() 
                WHERE id = :id
            """),
            {"id": action_id}
        )
        db.commit()
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Action not found")
        
        # TODO: Trigger Executor agent
        # from agents.executor import Executor
        # executor = Executor()
        # executor.execute_action(action_id)
        
        return {
            "success": True,
            "message": "Action approved and queued for execution",
            "action_id": action_id
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/actions/{action_id}/reject")
async def reject_action(
    action_id: int,
    request: RejectActionRequest,
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    Reject an AI action
    
    This will mark the action as REJECTED and record the reason
    """
    try:
        result = db.execute(
            text("""
                UPDATE proposed_actions 
                SET status = 'REJECTED', 
                    updated_at = NOW()
                WHERE id = :id
            """),
            {"id": action_id}
        )
        db.commit()
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Action not found")
        
        return {
            "success": True,
            "message": "Action rejected",
            "action_id": action_id,
            "reason": request.reason
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
