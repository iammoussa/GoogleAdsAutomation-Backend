# -*- coding: utf-8 -*-
"""
Alerts Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional

from api.models.schemas import AlertResponse
from database.database import get_db
from api.dependencies import verify_token

router = APIRouter()

@router.get("/alerts", response_model=List[AlertResponse])
async def get_alerts(
    resolved: Optional[bool] = Query(False, description="Filter by resolved status"),
    severity: Optional[str] = Query(None, description="Filter by severity (CRITICAL, WARNING, INFO)"),
    limit: int = Query(50, description="Max alerts to return"),
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    Get list of alerts
    
    Query params:
    - resolved: Filter by resolved status (default: false)
    - severity: Filter by severity (CRITICAL, WARNING, INFO)
    - limit: Max alerts to return (default 50)
    """
    try:
        query = """
            SELECT 
                a.id,
                a.campaign_id,
                cm.campaign_name,
                a.alert_type,
                a.message,
                a.created_at,
                a.resolved,
                cm.ctr as metric_value
            FROM alerts a
            JOIN campaign_metrics cm ON a.campaign_id = cm.campaign_id
            WHERE a.resolved = :resolved
        """
        
        params = {"resolved": resolved}
        
        # TODO: Add severity filter when column exists in alerts table
        # if severity:
        #     query += " AND a.severity = :severity"
        #     params["severity"] = severity
        
        query += " ORDER BY a.created_at DESC LIMIT :limit"
        params["limit"] = limit
        
        result = db.execute(text(query), params)
        alerts = []
        
        # Map alert types to severity
        severity_map = {
            "LOW_ROAS": "CRITICAL",
            "HIGH_CPC": "WARNING",
            "LOW_CTR": "WARNING",
            "BUDGET_OVERSPEND": "CRITICAL",
            "LOW_CONVERSIONS": "WARNING",
            "HIGH_COST_PER_CONVERSION": "WARNING"
        }
        
        # Map alert types to target values
        target_map = {
            "LOW_ROAS": 1.5,
            "HIGH_CPC": 0.60,
            "LOW_CTR": 2.0
        }
        
        for row in result:
            alert_severity = severity_map.get(row.alert_type, "INFO")
            
            # Filter by severity if specified
            if severity and alert_severity != severity:
                continue
            
            alerts.append(AlertResponse(
                id=row.id,
                campaign_id=row.campaign_id,
                campaign_name=row.campaign_name,
                alert_type=row.alert_type,
                severity=alert_severity,
                message=row.message,
                metric_value=float(row.metric_value or 0) if row.metric_value else None,
                metric_target=target_map.get(row.alert_type),
                created_at=row.created_at,
                resolved=row.resolved
            ))
        
        return alerts
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching alerts: {str(e)}")

@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """Mark an alert as resolved"""
    try:
        result = db.execute(
            text("UPDATE alerts SET resolved = true, updated_at = NOW() WHERE id = :id"),
            {"id": alert_id}
        )
        db.commit()
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return {"success": True, "message": "Alert resolved"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
